use crossbeam_channel::{unbounded, Receiver, Sender};
use std::sync::LazyLock;
use tracing::field::{Field, Visit};
use tracing::Event;
use tracing_subscriber::layer::Context;
use tracing_subscriber::Layer;

/// A log record buffered in the channel
pub struct LogRecord {
    pub level: u8,
    pub target: String,
    pub message: String,
}

/// Channel for buffering log records (safe to use without GIL)
static LOG_CHANNEL: LazyLock<(Sender<LogRecord>, Receiver<LogRecord>)> =
    LazyLock::new(|| unbounded());

/// Custom tracing Layer that pushes log records into a channel
pub struct ChannelLogLayer;

impl<S: tracing::Subscriber> Layer<S> for ChannelLogLayer {
    fn on_event(&self, event: &Event<'_>, _ctx: Context<'_, S>) {
        let metadata = event.metadata();
        let level = match *metadata.level() {
            tracing::Level::ERROR => 0u8,
            tracing::Level::WARN => 1,
            tracing::Level::INFO => 2,
            tracing::Level::DEBUG => 3,
            tracing::Level::TRACE => 4,
        };

        let mut visitor = MessageVisitor::default();
        event.record(&mut visitor);

        let record = LogRecord {
            level,
            target: metadata.target().to_string(),
            message: visitor.message,
        };

        // Non-blocking send - drop if channel is full (shouldn't happen with unbounded)
        let _ = LOG_CHANNEL.0.send(record);
    }
}

#[derive(Default)]
struct MessageVisitor {
    message: String,
}

impl Visit for MessageVisitor {
    fn record_debug(&mut self, field: &Field, value: &dyn std::fmt::Debug) {
        if field.name() == "message" {
            self.message = format!("{:?}", value);
        } else if self.message.is_empty() {
            self.message = format!("{} = {:?}", field.name(), value);
        } else {
            self.message
                .push_str(&format!(", {} = {:?}", field.name(), value));
        }
    }

    fn record_str(&mut self, field: &Field, value: &str) {
        if field.name() == "message" {
            self.message = value.to_string();
        } else if self.message.is_empty() {
            self.message = format!("{} = {}", field.name(), value);
        } else {
            self.message
                .push_str(&format!(", {} = {}", field.name(), value));
        }
    }
}

/// Initialize the tracing subscriber with channel-based log layer
pub fn init_subscriber(filter: &str) {
    use tracing_subscriber::prelude::*;
    use tracing_subscriber::EnvFilter;

    let env_filter = EnvFilter::try_new(filter).unwrap_or_else(|_| EnvFilter::new("warn"));

    tracing_subscriber::registry()
        .with(env_filter)
        .with(ChannelLogLayer)
        .init();
}

/// Drain all buffered log records
pub fn drain_logs() -> Vec<LogRecord> {
    let mut records = Vec::new();
    while let Ok(record) = LOG_CHANNEL.1.try_recv() {
        records.push(record);
    }
    records
}

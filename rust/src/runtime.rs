use std::sync::LazyLock;

use log::info;

pub static RUNTIME: LazyLock<tokio::runtime::Runtime> = LazyLock::new(|| {
    info!("Initializing Tokio multi-thread runtime");
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .unwrap_or_else(|e| {
            eprintln!("FATAL: Failed to create Tokio runtime: {}", e);
            std::process::exit(1);
        })
});

#[cfg(feature = "profiling")]
use std::alloc::{GlobalAlloc, Layout, System};
use std::sync::atomic::{AtomicUsize, Ordering};

use pyo3::prelude::*;
use pyo3::types::PyDict;

static BYTES_ALLOCATED: AtomicUsize = AtomicUsize::new(0);
static BYTES_DEALLOCATED: AtomicUsize = AtomicUsize::new(0);
static ALLOC_COUNT: AtomicUsize = AtomicUsize::new(0);
static DEALLOC_COUNT: AtomicUsize = AtomicUsize::new(0);
static PEAK_BYTES: AtomicUsize = AtomicUsize::new(0);

#[cfg(feature = "profiling")]
pub struct TrackingAllocator;

#[cfg(feature = "profiling")]
unsafe impl GlobalAlloc for TrackingAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let size = layout.size();
        let ptr = unsafe { System.alloc(layout) };
        if !ptr.is_null() {
            BYTES_ALLOCATED.fetch_add(size, Ordering::Relaxed);
            ALLOC_COUNT.fetch_add(1, Ordering::Relaxed);
            let active = BYTES_ALLOCATED
                .load(Ordering::Relaxed)
                .saturating_sub(BYTES_DEALLOCATED.load(Ordering::Relaxed));
            let mut peak = PEAK_BYTES.load(Ordering::Relaxed);
            while active > peak {
                match PEAK_BYTES.compare_exchange_weak(
                    peak,
                    active,
                    Ordering::Relaxed,
                    Ordering::Relaxed,
                ) {
                    Ok(_) => break,
                    Err(actual) => peak = actual,
                }
            }
        }
        ptr
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        BYTES_DEALLOCATED.fetch_add(layout.size(), Ordering::Relaxed);
        DEALLOC_COUNT.fetch_add(1, Ordering::Relaxed);
        unsafe { System.dealloc(ptr, layout) }
    }
}

#[cfg(feature = "profiling")]
#[global_allocator]
static GLOBAL: TrackingAllocator = TrackingAllocator;

#[pyfunction]
pub fn _get_memory_stats(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let allocated = BYTES_ALLOCATED.load(Ordering::Relaxed);
    let deallocated = BYTES_DEALLOCATED.load(Ordering::Relaxed);
    let active = allocated.saturating_sub(deallocated);
    let dict = PyDict::new(py);
    dict.set_item("total_allocated_bytes", allocated)?;
    dict.set_item("total_deallocated_bytes", deallocated)?;
    dict.set_item("active_bytes", active)?;
    dict.set_item("peak_bytes", PEAK_BYTES.load(Ordering::Relaxed))?;
    dict.set_item("allocation_count", ALLOC_COUNT.load(Ordering::Relaxed))?;
    dict.set_item("deallocation_count", DEALLOC_COUNT.load(Ordering::Relaxed))?;
    Ok(dict.into_any().unbind())
}

#[pyfunction]
pub fn _reset_memory_stats() {
    BYTES_ALLOCATED.store(0, Ordering::Relaxed);
    BYTES_DEALLOCATED.store(0, Ordering::Relaxed);
    ALLOC_COUNT.store(0, Ordering::Relaxed);
    DEALLOC_COUNT.store(0, Ordering::Relaxed);
    PEAK_BYTES.store(0, Ordering::Relaxed);
}

pub fn register_profiling_functions(m: &pyo3::Bound<'_, pyo3::types::PyModule>) -> PyResult<()> {
    m.add_function(pyo3::wrap_pyfunction!(_get_memory_stats, m)?)?;
    m.add_function(pyo3::wrap_pyfunction!(_reset_memory_stats, m)?)?;
    Ok(())
}

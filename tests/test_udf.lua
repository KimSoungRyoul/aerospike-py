-- Test UDF module for integration tests
function echo(rec, val)
    return val
end

function add(rec, a, b)
    return a + b
end

function get_bin(rec, bin_name)
    return rec[bin_name]
end

function set_bin(rec, bin_name, val)
    rec[bin_name] = val
    aerospike:update(rec)
    return 0
end

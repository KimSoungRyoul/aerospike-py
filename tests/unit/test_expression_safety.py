"""Tests for expression filter safety: input validation, depth limits, builder correctness."""

import pytest

from aerospike_py import exp


class TestUnaryFunctionsMissingArgs:
    @pytest.mark.parametrize(
        "fn",
        [exp.num_abs, exp.num_floor, exp.num_ceil, exp.to_int, exp.to_float, exp.int_not, exp.int_count],
        ids=["num_abs", "num_floor", "num_ceil", "to_int", "to_float", "int_not", "int_count"],
    )
    def test_unary_no_args_raises_type_error(self, fn):
        with pytest.raises(TypeError):
            fn()


class TestBinaryFunctionsMissingArgs:
    @pytest.mark.parametrize(
        "fn",
        [exp.num_mod, exp.num_pow, exp.num_log, exp.int_lshift, exp.int_rshift, exp.int_arshift],
        ids=["num_mod", "num_pow", "num_log", "int_lshift", "int_rshift", "int_arshift"],
    )
    def test_binary_no_args_raises_type_error(self, fn):
        with pytest.raises(TypeError):
            fn()

    @pytest.mark.parametrize(
        "fn",
        [exp.num_mod, exp.num_pow, exp.num_log, exp.int_lshift, exp.int_rshift],
        ids=["num_mod", "num_pow", "num_log", "int_lshift", "int_rshift"],
    )
    def test_binary_one_arg_raises_type_error(self, fn):
        with pytest.raises(TypeError):
            fn(exp.int_val(1))


class TestComparisonFunctionsMissingArgs:
    @pytest.mark.parametrize(
        "fn",
        [exp.eq, exp.ne, exp.gt, exp.ge, exp.lt, exp.le],
        ids=["eq", "ne", "gt", "ge", "lt", "le"],
    )
    def test_comparison_no_args_raises_type_error(self, fn):
        with pytest.raises(TypeError):
            fn()

    @pytest.mark.parametrize(
        "fn",
        [exp.eq, exp.ne, exp.gt, exp.ge, exp.lt, exp.le],
        ids=["eq", "ne", "gt", "ge", "lt", "le"],
    )
    def test_comparison_one_arg_raises_type_error(self, fn):
        with pytest.raises(TypeError):
            fn(exp.int_val(1))


class TestDepthLimit:
    def test_deep_nesting_produces_valid_structure(self):
        """Build 50-level nested expression — verifies no Python-side limit."""
        e = exp.int_val(1)
        for _ in range(50):
            e = exp.num_abs(e)
        assert e["__expr__"] == "num_abs"

    def test_very_deep_nesting_still_builds(self):
        """Build 200-level nested expression — Python builder has no limit,
        Rust parser enforces 128 depth limit when expression is used in policy."""
        e = exp.int_val(1)
        for _ in range(200):
            e = exp.num_abs(e)
        assert e["__expr__"] == "num_abs"
        assert "exprs" in e
        assert len(e["exprs"]) == 1


class TestNormalOperationSmoke:
    def test_basic_comparison(self):
        e = exp.gt(exp.int_bin("age"), exp.int_val(21))
        assert e["__expr__"] == "gt"
        assert e["left"]["__expr__"] == "int_bin"
        assert e["right"]["__expr__"] == "int_val"

    def test_logical_and(self):
        e = exp.and_(
            exp.gt(exp.int_bin("age"), exp.int_val(18)),
            exp.lt(exp.int_bin("age"), exp.int_val(65)),
        )
        assert e["__expr__"] == "and"
        assert len(e["exprs"]) == 2

    def test_logical_or(self):
        e = exp.or_(
            exp.eq(exp.string_bin("s"), exp.string_val("a")),
            exp.eq(exp.string_bin("s"), exp.string_val("b")),
        )
        assert e["__expr__"] == "or"
        assert len(e["exprs"]) == 2

    def test_not(self):
        e = exp.not_(exp.bin_exists("x"))
        assert e["__expr__"] == "not"
        assert e["expr"]["__expr__"] == "bin_exists"

    def test_unary_with_valid_arg(self):
        e = exp.num_abs(exp.int_bin("x"))
        assert e["__expr__"] == "num_abs"
        assert e["exprs"][0]["__expr__"] == "int_bin"

    def test_binary_with_valid_args(self):
        e = exp.num_mod(exp.int_bin("x"), exp.int_val(10))
        assert e["__expr__"] == "num_mod"
        assert len(e["exprs"]) == 2

    def test_let_def_var(self):
        e = exp.let_(
            exp.def_("x", exp.int_bin("count")),
            exp.gt(exp.var("x"), exp.int_val(0)),
        )
        assert e["__expr__"] == "let"
        assert len(e["exprs"]) == 2

    def test_cond_expression(self):
        e = exp.cond(
            exp.gt(exp.int_bin("age"), exp.int_val(18)),
            exp.string_val("adult"),
            exp.string_val("minor"),
        )
        assert e["__expr__"] == "cond"
        assert len(e["exprs"]) == 3

    def test_regex_compare(self):
        e = exp.regex_compare("^test.*", 0, exp.string_bin("name"))
        assert e["__expr__"] == "regex_compare"
        assert e["regex"] == "^test.*"

    def test_variadic_with_many_args(self):
        e = exp.num_add(exp.int_val(1), exp.int_val(2), exp.int_val(3), exp.int_val(4))
        assert e["__expr__"] == "num_add"
        assert len(e["exprs"]) == 4


class TestOpValidation:
    def test_unknown_op_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown expression op"):
            exp._cmd("nonexistent_op")

    def test_empty_op_raises_value_error(self):
        with pytest.raises(ValueError):
            exp._cmd("")

    def test_valid_op_accepted(self):
        result = exp._cmd("int_val", val=42)
        assert result["__expr__"] == "int_val"
        assert result["val"] == 42

from behave import given, then, when
from behave.runner import Context


@given("nothing")
def step_impl(context: Context):
    pass


@when("{} do what {} have always done,")
def _(context: Context, _: str, __: str):
    pass


@then("{} get what {} have always got!")
def _(context: Context, _: str, __: str):
    pass

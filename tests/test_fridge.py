
from fridge import Fridge

def test_the_basics():
    f=Fridge()
    assert f.get_red_can()==0
    assert f.get_green_can()==0
    assert f.get_blue_can()==0
    f.incr_red_can()
    f.incr_can('green_can')
    f.incr_blue_can()
    assert f.get_red_can()==1
    assert f.get_green_can()==1
    assert f.get_blue_can()==1
    f.decr_can('red_can')
    assert f.get_red_can()==0
    f.decr_can('red_can')
    assert f.get_red_can()==0

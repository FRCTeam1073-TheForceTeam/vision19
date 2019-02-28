import json

class Foo:
    def __init__(self):
        self.x = 1
        self.y = 22
        self.name = "zanzibar"

foo = Foo()
print("TEST CLASS")
print(foo.x)
print(foo.name)

print(json.dumps(foo.__dict__))

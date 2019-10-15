import firefly.domain as ffd
from test_src.todo.domain.entity.todo_list import TodoList


c = (TodoList.c.name == 'foo') | (TodoList.c.name > 1)

print(c)
d = c.to_dict()
print(d)
a = ffd.BinaryOp.from_dict(d)
print(a)

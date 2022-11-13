from datetime import date
from views import Index, Contact, Goods, CreateCategory, CreateGood, CopyGood, GoodsList


# front controller
def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]



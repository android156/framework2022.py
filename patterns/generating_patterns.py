from copy import deepcopy
from quopri import decodestring

from patterns.behavioral_patterns import Subject


# порождающий паттерн Прототип
class GoodPrototype:
    # прототип товара
    def clone(self):
        return deepcopy(self)


# Пользователь

class User:
    def __init__(self, name):
        self.name = name
        self.goods = []


# товар
class Good(GoodPrototype, Subject):
    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.goods.append(self)
        self.users = []
        super().__init__()

    def __getitem__(self, item):
        return self.users[item]

    def add_user(self, user: User):
        self.users.append(user)
        user.goods.append(self)
        self.notify()


# фитинг
class Component(Good):
    pass


class Pipe(Good):
    pass


class GoodFactory:
    types = {
        'pipe': Pipe,
        'component': Component
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, category):
        return cls.types[type_](name, category)


# категория
class Category:
    auto_id = 0

    def __init__(self, name, category=None):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.goods = []

    def items_count(self):
        result = len(self.goods)
        if self.category:
            result += self.category.items_count()
        return result


# основной интерфейс проекта
class Engine:
    def __init__(self):
        self.goods = []
        self.categories = []
        self.users = []

    @staticmethod
    def create_user(name):
        return User(name)

    @staticmethod
    def create_good(type_, name, category):
        return GoodFactory.create(type_, name, category)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')

    def get_good(self, name):
        for item in self.goods:
            if item.name == name:
                return item
        return None

    def get_user(self, name) -> User:
        for item in self.users:
            if item.name == name:
                return item


# порождающий паттерн Синглтон
class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log--->', text)

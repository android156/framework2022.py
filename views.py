from my_framework.templator import render
from patterns.behavioral_patterns import CreateView, BaseSerializer, EmailNotifier, SmsNotifier, ListView
from patterns.generating_patterns import Engine, Logger
from patterns.structural_patterns import AppRoute, Debug

site = Engine()
logger = Logger('main')
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()

class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', objects_list=site.categories)


class Goods:
    def __call__(self, request):
        logger.log('Список товаров конкретной категории')
        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('goods.html',
                                    objects_list=category.goods,
                                    name=category.name,
                                    id=category.id,
                                    )
        except KeyError:
            return '200 OK', f'No goods have been added yet in category'


class GoodsList:
    def __call__(self, request):
        return '200 OK', render('goods_list.html', objects_list=site.categories)


class CreateCategory:
    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост

            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)
            print('Все категории: ', [(category.id, category.name) for category in site.categories])
            return '200 OK', render('index.html', objects_list=site.categories)
        else:
            categories = site.categories
            return '200 OK', render('create_category.html',
                                    categories=categories)


class CreateGood:
    category_id = -1

    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                good = site.create_good('pipe', name, category)

                good.observers.append(email_notifier)
                good.observers.append(sms_notifier)

                site.goods.append(good)
                # Для отладки
                # print('Все товары : ', [good.name for good in site.goods])
                # print('Имя категории: ', category.name)
                # print('Товары категории: ', [good.name for good in category.goods])

            return '200 OK', render('goods.html',
                                    objects_list=category.goods,
                                    name=category.name,
                                    id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create_good.html',
                                        name=category.name,
                                        id=category.id)
            except KeyError:
                return '200 OK', 'No categories have been added yet'


class CopyGood:
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']

            old_good = site.get_good(name)

            if old_good:
                category = old_good.category
                new_name = f'copy_{name}'
                new_good = old_good.clone()
                new_good.name = new_name
                new_good.category = category
                category.goods.append(new_good)

                print('Все товары : ', [good.name for good in site.goods])
                print('категория клона: ', new_good.category)
                print('категория оригинала: ', category)
                print('Имя категории клона: ', new_good.category.name)
                print('Имя категории оригинала: ', category.name)
                print('Все категории: ', [(category.id, category.name) for category in site.categories])
                print('Товары категории клона: ', [good.name for good in new_good.category.goods])
                print('Товары категории оригинала: ', [good.name for good in category.goods])

            return '200 OK', render('goods.html',
                                    objects_list=category.goods,
                                    name=new_good.category.name,
                                    id=new_good.category.id)
        except KeyError:
            return '200 OK', 'No goods have been added yet'


routes = {
    '/': Index(),
    # '/contact/': Contact(),
    '/goods/': Goods(),
    '/goods_list/': GoodsList(),
    '/create-category/': CreateCategory(),
    '/create-good/': CreateGood(),
    '/copy-good/': CopyGood(),
}


# контроллер 404
class NotFound404:
    @Debug(name='NotFound404')
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


@AppRoute(routes=routes, url='/contact/')
class Contact:
    @Debug(name='Contact')
    def __call__(self, request):
        return '200 OK', render('contact.html', data=request)


@AppRoute(routes=routes, url='/users-list/')
class UserListView(ListView):
    queryset = site.users
    template_name = 'users_list.html'


@AppRoute(routes=routes, url='/create-user/')
class UserCreateView(CreateView):
    template_name = 'create_user.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('user', name)
        site.users.append(new_obj)


@AppRoute(routes=routes, url='/add-user/')
class AddStudentByCourseCreateView(CreateView):
    template_name = 'add_user.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['goods'] = site.goods
        context['users'] = site.users
        return context

    def create_obj(self, data: dict):
        good_name = data['good_name']
        good_name = site.decode_value(good_name)
        good = site.get_good(good_name)
        user_name = data['user_name']
        user_name = site.decode_value(user_name)
        user = site.get_user(user_name)
        good.add_user(user)


@AppRoute(routes=routes, url='/api/')
class CourseApi:
    @Debug(name='GoodApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.goods).save()

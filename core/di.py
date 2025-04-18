class DIContainer:
    _instance = None  # Статическое поле для хранения экземпляра
    def __init__(self):
        self._services = {}  # Хранилище зарегистрированных сервисов
        self._instances = {}  # Кеш для синглтонов

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DIContainer()  # Создание единственного экземпляра
        return cls._instance
    def register(self, name, service, is_singleton=False):
        """Регистрация сервиса в контейнере"""
        self._services[name] = {
            'service': service,         #Класс или готовый экземпляр (например, EventBus или EventBus()
            'singleton': is_singleton   #Если True, сервис будет создан один раз и возвращаться при каждом resolve()
        }

    def resolve(self, name):
        """Получение экземпляра сервиса"""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")

        service_info = self._services[name]

        # Для синглтонов возвращаем существующий экземпляр
        if service_info['singleton']:
            if name not in self._instances:
                self._instances[name] = self._create_instance(service_info['service'])
            return self._instances[name]

        # Для transient создаём новый экземпляр
        return self._create_instance(service_info['service'])

    def _create_instance(self, service):
        """Создание экземпляра с автоматическим внедрением зависимостей"""
        if callable(service):
            # Анализ параметров конструктора
            params = self._get_constructor_params(service)
            dependencies = {
                name: self.resolve(name)
                for name in params
            }
            return service(**dependencies)
        return service  # Если это уже экземпляр

    def _get_constructor_params(self, cls):
        """Получение параметров конструктора класса"""
        import inspect
        signature = inspect.signature(cls.__init__)
        return [
            param.name
            for param in signature.parameters.values()
            if param.name != 'self' and param.default == param.empty
        ]
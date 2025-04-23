"""
Модуль для реализации контейнера внедрения зависимостей (DI Container).

Контейнер предоставляет:
- Регистрацию сервисов (как синглтонов, так и transient)
- Автоматическое разрешение зависимостей
- Глобальный доступ через get_instance() (реализация Singleton)
"""
import inspect


class DIContainer:
    """Контейнер внедрения зависимостей (Dependency Injection Container).

        Реализует паттерн Singleton и предоставляет:
        - Хранение зарегистрированных сервисов
        - Создание экземпляров с автоматическим внедрением зависимостей
        - Поддержку как синглтонов, так и transient-сервисов

        Пример использования:
            >>> container = DIContainer.get_instance()
            >>> container.register('event_bus', EventBus, is_singleton=True)
            >>> bus = container.resolve('event_bus')
    """
    _instance = None  # Статическое поле для хранения экземпляра

    def __init__(self):
        """Инициализирует новый контейнер зависимостей."""
        self._services = {}  # Хранилище зарегистрированных сервисов
        self._instances = {}  # Кеш для синглтонов

    @classmethod
    def get_instance(cls):
        """Возвращает единственный экземпляр контейнера (реализация Singleton)."""
        if cls._instance is None:
            cls._instance = DIContainer()  # Создание единственного экземпляра
        return cls._instance

    def register(self, name, service, is_singleton=False):
        """Регистрирует сервис в контейнере.

        Args:
            name (str): Имя сервиса для последующего разрешения
            service (callable/object): Класс или готовый экземпляр
            is_singleton (bool): Если True, сервис будет создан только один раз
        """
        self._services[name] = {
            # Класс или готовый экземпляр (например, EventBus или EventBus())
            'service': service, 'singleton': is_singleton
            # Если True, сервис будет создан один раз и возвращаться при каждом resolve()
        }

    def resolve(self, name):
        """Создает и возвращает экземпляр сервиса с внедренными зависимостями.

        Args:
            name (str): Имя зарегистрированного сервиса

        Returns:
            object: Экземпляр запрошенного сервиса

        Raises:
            ValueError: Если сервис не зарегистрирован
        """
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
    # понять почему медод _get_constructor_params должен быть статическим(нужно это мне)

    def _get_constructor_params(self, cls):
        """Получение параметров конструктора класса.

        Args:
            cls: Класс, параметры конструктора которого нужно проанализировать

        Returns:
            List[str]: Список имен обязательных параметров конструктора
    """
        signature = inspect.signature(cls.__init__)
        return [
            param.name
            for param in signature.parameters.values()
            if param.name != 'self' and param.default == param.empty
        ]

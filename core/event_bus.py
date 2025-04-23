"""
Модуль для реализации шины событий (Event Bus).

Шина событий позволяет компонентам подписываться на события и получать уведомления,
когда эти события происходят.
"""
import typing

class EventBus:
    """Реализация шины событий (Event Bus) для подписки и публикации событий.

        Позволяет:
        - Подписываться на события (`subscribe`)
        - Отписываться от событий (`unsubscribe`)
        - Публиковать события (`publish`), уведомляя всех подписчиков

        Пример использования:
            >>> bus = EventBus()
            >>> bus.subscribe("message", lambda msg: print(f"Получено: {msg}"))
            >>> bus.publish("message", "Привет, мир!")  # Выведет: Получено: Привет, мир!
        """
    def __init__(self):
        self._subscribers: typing.Dict[str, typing.List[typing.Callable]] = {}

    def subscribe(self, event_type: str, callback: typing.Callable):
        """Подписаться на событие.

                Args:
                    event_type (str): Тип события, на которое подписываемся.
                    callback (Callable): Функция, которая будет вызвана при публикации события.
                """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: typing.Callable):
        """"Отписаться от события.

        Args:
            event_type (str): Тип события, от которого отписываемся.
            callback (Callable): Функция, которую нужно удалить из подписчиков.
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

    def publish(self, event_type: str, *args, **kwargs):
        """Опубликовать событие, уведомив всех подписчиков.

        Args:
            event_type (str): Тип публикуемого события.
            *args: Аргументы, передаваемые в callback-функции подписчиков.
            **kwargs: Именованные аргументы для callback-функций.
        """
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(*args, **kwargs)

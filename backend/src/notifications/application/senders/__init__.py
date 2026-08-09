"""
Реестр и управление жизненным циклом отправителей уведомлений.

Модуль предоставляет инфраструктурный registry для channel-specific
NotificationSender. Каждый тип канала регистрирует реализацию sender и
Pydantic-схему конфигурации, которая используется для валидации параметров
NotificationChannel.params.

Sender отвечает за адаптацию доменного уведомления к конкретному каналу:
получает Notification и ContactPoint, создаёт запрос необходимого формата
и передаёт его транспортному клиенту.

BaseNotificationSender дополнительно управляет жизненным циклом клиента.
Клиент создаётся лениво при первом вызове send() и переиспользуется
последующими отправками. Это позволяет не создавать новый connection pool
или HTTP/SMTP-соединение для каждого уведомления.

Registry хранит sender не только по типу канала, но и по идентификатору
конкретного Channel. Это необходимо, поскольку несколько каналов одного
типа могут иметь разные параметры подключения, например несколько SMTP
серверов или Telegram-ботов.

При получении sender registry:

1. Находит зарегистрированную реализацию для ChannelType.
2. Валидирует Channel.params соответствующей Pydantic-моделью.
3. Проверяет существующий sender для Channel.id.
4. Возвращает его, если конфигурация не изменилась.
5. При изменении конфигурации закрывает старый sender и создаёт новый.

Таким образом, NotificationService не знает ни о конкретных sender, ни
о формате их конфигурации, ни о транспортных клиентах.

Архитектура:

    NotificationService
            │
            ▼
       get_sender()
            │
            ▼
    Sender registry
            │
            ├── ChannelType.EMAIL ──► EmailSender
            │                              │
            │                              ▼
            │                         EmailClient
            │
            └── ChannelType.TELEGRAM ► TelegramSender
                                           │
                                           ▼
                                      TelegramClient

Sender является адаптером между доменной моделью уведомления и конкретным
транспортом. Transport client, в свою очередь, отвечает только за работу
с внешним API или протоколом доставки.

Для добавления нового канала достаточно зарегистрировать новую реализацию:

    @register_sender(ChannelType.EMAIL, config=EmailConfig)
    class EmailSender(BaseNotificationSender[EmailConfig, EmailClient]):
        ...

Конфигурация канала при этом остаётся динамической и хранится в
NotificationChannel.params, а её структура контролируется соответствующей
Pydantic-моделью sender.
"""


from .base import get_sender
from .email import EmailNotificationSender

__all__ = ["EmailNotificationSender", "get_sender"]

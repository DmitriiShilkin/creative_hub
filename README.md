## Выполненные задачи для веб-приложения creative-hub в рамках стажировки в Antipoff Group:

### Тесты:
1. Для endpoints USER EXPERIENCE, плюс фикстуры, для моделей Country, City 
добавлены схемы CreateDB.
2. Для endpoints Calendar Events, Calendar Comments, плюс фикстуры.
3. В тест API test_user_info добавлены 2 теста без схемы PrivateSite, написана
фикстура PrivateSite.
4. В тест API test_user_education добавлены тесты.
5. Для endpoints ProfileCompleteness добавлена фикстура и тесты API.
6. Для endpoints UserUpdate добавлен тест таймзон.
7. Для endpoints Mentorship изменена фикстура, изменены тесты API.
8. Для endpoints User Catalog добавлены тесты API.
9. Для endpoints User Specialization изменена фикстура, изменены тесты API.
10. Для endpoints Favorite Jobs добавлена фикстура и тесты API, 
изменены сопутствующие фикстуры.

### Разработка:
1. Исправлен crud для удаления в endpoint Delete Proposal.
2. Исправлены ненаходящиеся Job в endpoints Post/Update/Delete Contact Person Job.
3. Проведен рефакторинг констант для UserExperience, Education, crud_types.
4. BaseAsyncCRUD разделен на 4 миксина, проведена проверка работы всех endpoints,
в crud Job, User добавлена подгрузка связанных моделей.
5. Найден и исправлен баг - у модели User атрибут birthday имел тип datetimetz,
исправлен на date, написана и протестирована миграция.
6. В моделях UserExperience и Education для атрибутов start_month, end_month 
тип Month заменен на integer, написана и протестирована миграция, 
в схемы добавлены валидаторы, исправлены тесты и фикстуры.
7. В модели User исправлены типы данных для связей с внешними моделями
social_networks, links, experience. Скорректирована схема UserResponseFull для
атрибута private_site.
8. Исправлена работа валидаторов UserExperience, Education и сообщения для
вызывамых исключений, исправлен перехват исключений для Education.
9. Исправлена работа валидатора для схемы ExperienceUpdate.
10. В crud ReadAsync, CRUDUser, utilies.tokens исправлены типы uid: str на uid: UUID.
11. Поля link_id, social_network_id заменены на id в схеме, сервисах и тестах user_info.
12. Добавлены endpoints Calendar Events, Calendar Comments. Разработаны модели CalendarEvent, 
CalendarComment, константы, CRUD, сервисы, схемы и валидаторы для них. Добавлена поддержка
в модель, схему и CRUD User. Добавлен вью для админки.
13. В endpoint UserInfo PUT добавлен PrivateSite, изменена схема, переписан сервис 
для создания и обновления PrivateSite.
14. Добавлен эндпоинт для одиночного частичного обновления User Education,
создан отдельный сервис, создана отдельная схема, и добавлен отдельный круд update.
15. Добавлен эндпоинт для для чтения и частичного обновления User ProfileCompleteness,
создана модель, схемы, роуты, круды, миграция, сервис.
16. В модель User добавлена связь с моделью Timezone, изменены схемы UserUpdate, UserResponse,
UserResponseFull, создана миграция, в crud_user добавлена подгрузка связанной модели,
в endpoints UserUpdate добавлена проверка несуществующей таймзоны.
17. В модель Mentorship добавлен атрибут is_show, изменены схемы, создана миграция.
18. Добавлена константа для выборочной подгрузки данных из модели UserExperience,
изменены схемы UserCatalog, в схемы UserExperience добавлена ExperienceCatalogResponse,
в crud добавлена подгрузка experience.
19. В модель UserSpecialization добавлены атрибуты price, currency, payment_per,
is_ready_to_move, is_ready_for_remote_work. Добавлены атрибуты в схемы, добавлен валидатор.
Написана миграция.
20. Для карточек Job добавлен признак "Просмотрено" в ленте. Поменялся круд и схема.
21. Созданы эндпоинты Favorite Jobs для просмотра, добавления и удаления работ из избранного,
изменены модели Favorite и Job, схемы, CRUDFavorite, CRUDJob, сервис Job, написана
миграция.
22. Проведен рефакторинг методов CRUDFavorite, приведены в соответствие фикстуры и роуты.
23. Проведен рефакторинг методов CRUDEvent - get_with_counters выделены в отдельный CRUD,
внесены соответствующие изменения в роут и сервис.
24. Исправлено нарушение уникальности при создании EventView,
исправлено получение events по author_id,
добавлено ограничение уникальности (ip_address, event_id) для EventView,
создана миграция.
25. В схемах Event extra_languages сделаны обязательными
добавлена типизация, исправлены несоответствия PEP.

#### Используемые инструменты:
1. Python v3.11;
2. FastAPI v0.103.2;
3. Pytest v7.4.4;
4. Docker v4.27.2;
5. Gitlab;
6. Pre-commit v3.6.0.
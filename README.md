## Выполненные задачи для веб-приложения creative-hub в рамках стажировки в Antipoff Group:

### Тесты:
1. Для endpoints USER EXPERIENCE, плюс фикстуры, для моделей Country, City 
добавлены схемы CreateDB.

### Разработка:
1. Исправлен crud для удаления в endpoint Delete Proposal.
2. Исправлены ненаходящиеся Job в endpoints Post/Update/Delete Contact Person Job.
3. Проведен рефакторинг констант для UserExperience, Education, crud_types.
4. BaseAsyncCRUD разделен на 4 миксина, проведена проверка работы всех endpoints.
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

#### Используемые инструменты:
1. Python v3.11;
2. FastAPI v0.103.2;
3. Pytest v7.4.4;
4. Docker v4.27.2;
5. Gitlab;
6. Pre-commit v3.6.0.
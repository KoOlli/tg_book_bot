# Continuous development

## Зачем нужен CD

**CD** - **Continuous development** - нужно для того, чтобы разработка продолжалась без проблем даже после деплоя очередной версии приложения. Для того, чтобы осуществить "продолжительную разработку" в *GitLab* нужно создать файл `gitlab-ci.yml`.

Грубо говоря, **CD** проверяет, соответствует ли проект нормам, определённым самим программистом. В **CD** входят различные стилевые тесты, тесты на утечки, статические тесты и другие подобные махинации с исходным кодом проекта.

Примерные стадии в файле `gitlab-ci.yml`:

- `style_tests`
- `leaks_tests`
- `static_tests`
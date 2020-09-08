{% extends 'sql/update.sql' %}
    {% block fqtn %}{{ fqtn.replace('.', '_') | sqlsafe }}{% endblock %}
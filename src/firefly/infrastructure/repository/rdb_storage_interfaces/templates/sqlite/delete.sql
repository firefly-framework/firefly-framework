{% extends 'sql/delete.sql' %}
    {% block fqtn %}{{ fqtn.replace('.', '_') | sqlsafe }}{% endblock %}
{% extends 'sql/drop_column.sql' %}
    {% block fqtn %}{{ fqtn.replace('.', '_') | sqlsafe }}{% endblock %}
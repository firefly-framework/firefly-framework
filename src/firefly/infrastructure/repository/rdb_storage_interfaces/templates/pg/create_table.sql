{% extends 'sql/create_table.sql' %}

{% block id_type %}
    {% if f.length %}
        {% if f.length == 36 %}
            uuid
        {% else %}
            varchar({{ f.length | sqlsafe }})
        {% endif %}
    {% else %}
        varchar(255)
    {% endif %}
{% endblock %}

{% block json_type %}{% if f.name == '__document' %}text{% else %}jsonb{% endif %}{% endblock %}
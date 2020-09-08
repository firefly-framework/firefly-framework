{% extends 'sql/create_table.sql' %}
    {% block id_type %}
        {% if 'length' in f.metadata %}
            {% if f.metadata['length'] == 36 %}
                uuid
            {% else %}
                varchar({{ f.metadata['length'] | sqlsafe }})
            {% endif %}
        {% else %}
            varchar(256)
        {% endif %}
    {% endblock %}
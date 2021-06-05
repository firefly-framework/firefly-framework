alter table {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %}

add column {{ _q | sqlsafe }}{{ column.name | sqlsafe }}{{ _q | sqlsafe }}

    {% if column.string_type == 'int' %}
        {% block int_type scoped %} integer {% endblock %}
    {% elif column.string_type == 'float' %}
        {% block float_type scoped %} float {% endblock %}
    {% elif column.string_type == 'bool' %}
        {% block bool_type scoped %} boolean {% endblock %}
    {% elif column.string_type == 'bytes' %}
        {% block bytes_type scoped %} blob {% endblock %}
    {% elif column.string_type == 'datetime' %}
        {% block datetime_type scoped %} datetime {% endblock %}
    {% else %}
        {% if column.length %}
            {% block varchar_type scoped %} varchar ({{ column.length | sqlsafe }}) {% endblock %}
        {% else %}
            {% block text_type scoped %} text{% endblock %}
        {% endif %}
    {% endif %}
        {% if column.default is not none %}
        default
        {% if column.default is string %}'{% endif %}{{ column.default | sqlsafe }}{% if column.default is string %}'{% endif %}
    {% endif %}
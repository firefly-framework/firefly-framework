create table {% block create_condition %}if not exists{% endblock %} {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %} (
    {% block column_list %}
        {% for k, v in fields(entity) %}
            {% block column_name scoped %} "{{ k | sqlsafe }}" {% endblock %}
            {% if k.type == 'int' %}
                {% block int_type scoped %}integer{% endblock %}
            {% elif k.type == 'float' %}
                {% block float_type scoped %}float{% endblock %}
            {% elif k.type == 'bool' %}
                {% block bool_type scoped %}boolean{% endblock %}
            {% elif k.type == 'bytes' %}
                {% block bytes_type scoped %}blob{% endblock %}
            {% elif k.type == 'datetime' %}
                {% block datetime_type scoped %}datetime{% endblock %}
            {% else %}
                {% if 'length' in v.metadata %}
                    {% block varchar_type scoped %}varchar({{ v.metadata['length'] }}){% endblock %}
                {% else %}
                    {% block text_type scoped %}text{% endblock %}
                {% endif %}
            {% endif %}
        {% endfor %}
    {% endblock %}
)

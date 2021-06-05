create table {% block create_condition %}if not exists{% endblock %} {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %} (
    {% block column_list %}
        {% for f in mapped_fields(entity) %}
            {% block column_name scoped %} {{ _q | sqlsafe }}{{ f.name | sqlsafe }}{{ _q | sqlsafe }} {% endblock %}
            {% if f.index() %}
                {% block id_type scoped %}
                    {% if f.length %}
                        varchar{{ '(' | sqlsafe }}{{ f.length | sqlsafe }}{{ ')' | sqlsafe }}
                    {% else %}
                        varchar(255)
                    {% endif %}
                {% endblock %}
            {% elif f.string_type == 'int' %}
                {% block int_type scoped %}integer{% endblock %}
            {% elif f.string_type == 'float' %}
                {% block float_type scoped %}float{% endblock %}
            {% elif f.string_type == 'bool' %}
                {% block bool_type scoped %}boolean{% endblock %}
            {% elif f.string_type == 'bytes' %}
                {% block bytes_type scoped %}blob{% endblock %}
            {% elif f.string_type == 'datetime' %}
                {% block datetime_type scoped %}datetime{% endblock %}
            {% elif (f.string_type == 'dict' or f.string_type == 'list') %}
                {% block json_type scoped %}text{% endblock %}
            {% else %}
                {% if f.length %}
                    {% block varchar_type scoped %}varchar({{ f.length | sqlsafe }}){% endblock %}
                {% else %}
                    {% block text_type scoped %}text{% endblock %}
                {% endif %}
            {% endif %}
            {% if f.default is not none %}
                default
                {% if f.default is string %}'{% endif %}{{ f.default | sqlsafe }}{% if f.default is string %}'{% endif %}
            {% endif %}
            {% if not loop.last %},{% endif %}
        {% endfor %}

        {% block primary_key %}
            , primary key (
        {% if entity.id_name() is string %}
            {{ _q | sqlsafe }}{{ entity.id_name() | sqlsafe }}{{ _q | sqlsafe }}
        {% else %}
            {% for c in entity.id_name() %}
                {{ _q | sqlsafe }}{{ c | sqlsafe }}{{ _q | sqlsafe }}{% if not loop.last %},{% endif %}
            {% endfor %}
        {% endif %}
            )
        {% endblock %}
    {% endblock %}
)

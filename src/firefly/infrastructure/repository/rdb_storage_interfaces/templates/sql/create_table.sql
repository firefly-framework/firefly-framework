create table {% block create_condition %}if not exists{% endblock %} {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %} (
    {% block column_list %}
        {% for f in mapped_fields(entity) %}
            {% block column_name scoped %} {{ _q | sqlsafe }}{{ f.name | sqlsafe }}{{ _q | sqlsafe }} {% endblock %}
            {% if f.is_id %}
                {% block id_type scoped %}
                    {% if f.length %}
                        varchar{{ '(' | sqlsafe }}{{ f.length | sqlsafe }}{{ ')' | sqlsafe }}
                    {% else %}
                        varchar(256)
                    {% endif %}
                {% endblock %}
            {% elif f.type == 'int' %}
                {% block int_type scoped %}integer{% endblock %}
            {% elif f.type == 'float' %}
                {% block float_type scoped %}float{% endblock %}
            {% elif f.type == 'bool' %}
                {% block bool_type scoped %}boolean{% endblock %}
            {% elif f.type == 'bytes' %}
                {% block bytes_type scoped %}blob{% endblock %}
            {% elif f.type == 'datetime' %}
                {% block datetime_type scoped %}datetime{% endblock %}
            {% else %}
                {% if 'length' in f.metadata %}
                    {% block varchar_type scoped %}varchar({{ f.metadata['length'] | sqlsafe }}){% endblock %}
                {% else %}
                    {% block text_type scoped %}text{% endblock %}
                {% endif %}
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

create table {% block create_condition %}if not exists{% endblock %} {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %} (
    {% block column_list %}
        {% block id_name scoped %}"{{ entity.id_name() | sqlsafe }}"{% endblock %}
            {% set f = entity | id_field %}
            {% block id_type scoped %}
                {% if 'length' in f.metadata %}
                    varchar({{ f.metadata['length'] }})
                {% else %}
                    varchar(256)
                {% endif %}
            {% endblock %},
        document {% block document_type %}text{% endblock %}
        {% block primary_key %}
            , primary key ("{{ entity.id_name() | sqlsafe }}")
        {% endblock %}
    {% endblock %}
)

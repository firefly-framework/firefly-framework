select name, type from PRAGMA_TABLE_INFO('{{ fqtn.replace('.', '_') | sqlsafe }}')
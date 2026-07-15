"""Tests para la validación de filtros."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.errors.handlers import ValidationError
from app.models import ConsultaItem
from app.validators.filters import validar_y_transformar_filtro, validar_consultas


class TestValidadores:
    """Tests de validación de filtros individuales y listas de filtros."""

    def test_filtro_genero_valido(self):
        """Verifica que los valores válidos de GENERO pasen la validación."""
        validos = ["No especificado", "Masculino", "Femenino", "Otro"]
        for valor in validos:
            filtro = ConsultaItem(consulta="GENERO", valor=valor)
            validar_y_transformar_filtro(filtro)

    def test_filtro_genero_invalido(self):
        """Verifica que un GENERO inválido lance ValidationError."""
        filtro = ConsultaItem(consulta="GENERO", valor="Invalido")
        with pytest.raises(ValidationError, match="no es válido para GENERO"):
            validar_y_transformar_filtro(filtro)

    def test_filtro_edad_valido(self):
        """Verifica que valores numéricos válidos de EDAD pasen la validación."""
        validos = ["0", "31", "100", "200"]
        for valor in validos:
            filtro = ConsultaItem(consulta="EDAD", valor=valor)
            validar_y_transformar_filtro(filtro)

    def test_filtro_edad_invalido_fuera_rango(self):
        """Verifica que edades fuera de rango lancen ValidationError."""
        invalidos = ["-1", "201"]
        for valor in invalidos:
            filtro = ConsultaItem(consulta="EDAD", valor=valor)
            with pytest.raises(ValidationError, match="entre 0 y 200"):
                validar_y_transformar_filtro(filtro)

    def test_filtro_edad_no_numerico(self):
        """Verifica que EDAD no numérica lance ValidationError."""
        filtro = ConsultaItem(consulta="EDAD", valor="treinta")
        with pytest.raises(ValidationError, match="no es un número entero válido"):
            validar_y_transformar_filtro(filtro)

    def test_filtro_canal_valido(self):
        """Verifica que los valores válidos de CANAL pasen la validación."""
        validos = ["POS", "WEB", "APP", "CCT", "APR", "WPR", "pos", "Web"]
        for valor in validos:
            filtro = ConsultaItem(consulta="CANAL", valor=valor)
            validar_y_transformar_filtro(filtro)

    def test_filtro_canal_invalido(self):
        """Verifica que un CANAL inválido lance ValidationError."""
        filtro = ConsultaItem(consulta="CANAL", valor="TIENDA")
        with pytest.raises(ValidationError, match="no es válido para CANAL"):
            validar_y_transformar_filtro(filtro)

    def test_filtro_codigo_producto_valido(self):
        """Verifica que un SKU numérico pase la validación."""
        filtro = ConsultaItem(consulta="CODIGO_PRODUCTO", valor="12345")
        validar_y_transformar_filtro(filtro)

    def test_filtro_codigo_producto_invalido(self):
        """Verifica que un SKU no numérico lance ValidationError."""
        filtro = ConsultaItem(consulta="CODIGO_PRODUCTO", valor="PROD1")
        with pytest.raises(ValidationError, match="no es un número entero válido"):
            validar_y_transformar_filtro(filtro)

    def test_filtro_id_persona_valido(self):
        """Verifica que un UUID pase la validación básica."""
        filtro = ConsultaItem(consulta="ID_PERSONA", valor="123e4567-e89b-12d3-a456-426614174000")
        validar_y_transformar_filtro(filtro)

    def test_filtro_id_persona_invalido(self):
        """Verifica que un UUID muy corto lance ValidationError."""
        filtro = ConsultaItem(consulta="ID_PERSONA", valor="corto")
        with pytest.raises(ValidationError, match="no es un identificador UUID válido"):
            validar_y_transformar_filtro(filtro)

    def test_filtro_local_valido(self):
        """Verifica que un local numérico pase la validación."""
        filtro = ConsultaItem(consulta="LOCAL", valor="123")
        validar_y_transformar_filtro(filtro)

    def test_filtro_local_invalido(self):
        """Verifica que un local no numérico lance ValidationError."""
        filtro = ConsultaItem(consulta="LOCAL", valor="L1")
        with pytest.raises(ValidationError, match="no es un número entero válido"):
            validar_y_transformar_filtro(filtro)

    def test_filtro_fecha_valida(self):
        """Verifica que fechas ISO-8601 pasen la validación."""
        validas = ["2023-01-01", "2023-01-01T12:00:00", "2023-01-01T12:00:00Z"]
        for consulta in ["FECHA_DESDE", "FECHA_HASTA"]:
            for valor in validas:
                filtro = ConsultaItem(consulta=consulta, valor=valor)
                validar_y_transformar_filtro(filtro)

    def test_filtro_fecha_invalida(self):
        """Verifica que fechas malformadas lancen ValidationError."""
        invalidas = ["01/01/2023", "2023", "hoy"]
        for consulta in ["FECHA_DESDE", "FECHA_HASTA"]:
            for valor in invalidas:
                filtro = ConsultaItem(consulta=consulta, valor=valor)
                with pytest.raises(ValidationError, match="no es una fecha válida"):
                    validar_y_transformar_filtro(filtro)

    def test_consulta_no_permitida(self):
        """Verifica que una consulta fuera de la lista blanca lance ValidationError."""
        filtro = ConsultaItem(consulta="DESCONOCIDO", valor="123")
        with pytest.raises(ValidationError, match="no es válido"):
            validar_y_transformar_filtro(filtro)

    def test_validar_lista_consultas_vacia(self):
        """Verifica que una lista de consultas vacía o nula lance ValidationError."""
        with pytest.raises(ValidationError, match="no puede estar vacío"):
            validar_consultas([])

        with pytest.raises(ValidationError, match="no puede estar vacío"):
            validar_consultas(None)

    def test_validar_consulta_sin_campo(self):
        """Verifica que un filtro sin campo 'consulta' definido falle en Pydantic."""
        with pytest.raises(PydanticValidationError):
            ConsultaItem(valor="123")

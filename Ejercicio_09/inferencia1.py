import re

REGISTRO_BASE = {
    "axiomas": [
        "Estudiante(Ana)", "Estudiante(Luis)", "Profesor(Marta)",
        "TieneCredencial(Ana)", "TieneCredencial(Marta)", "HorarioNocturno(Hoy)"
    ],
    "implicaciones": {
        "R_miembro_est": {"consecuente": "Miembro(x)", "antecedentes": ["Estudiante(x)", "TieneCredencial(x)"]},
        "R_miembro_prof": {"consecuente": "Miembro(x)", "antecedentes": ["Profesor(x)"]},
        "R_acceso": {"consecuente": "AccesoNoche(x)", "antecedentes": ["Miembro(x)", "HorarioNocturno(Hoy)"]},
        "R_beca": {"consecuente": "Becario(x)", "antecedentes": ["Estudiante(x)", "TieneCredencial(x)"]}
    }
}

def descomponer_literal(literal_texto):
    coincidencia = re.match(r"(\w+)\(([^)]+)\)", literal_texto)
    return coincidencia.group(1), coincidencia.group(2)

def es_identificador_variable(simbolo):
    return simbolo[0].islower()

def unificar_terminos(lit_a, lit_b, sustituciones):
    pred_a, arg_a = descomponer_literal(lit_a)
    pred_b, arg_b = descomponer_literal(lit_b)
    if pred_a != pred_b:
        return None
    
    mapeo = sustituciones.copy()
    if es_identificador_variable(arg_a):
        if arg_a in mapeo and mapeo[arg_a] != arg_b:
            return None
        mapeo[arg_a] = arg_b
    elif es_identificador_variable(arg_b):
        if arg_b in mapeo and mapeo[arg_b] != arg_a:
            return None
        mapeo[arg_b] = arg_a
    elif arg_a != arg_b:
        return None
    return mapeo

def instanciar_literal(literal_texto, sustituciones):
    pred, argumento = descomponer_literal(literal_texto)
    return f"{pred}({sustituciones.get(argumento, argumento)})"

def encadenar_hacia_adelante(base, lista_consultas):
    print("--- ENCADENAMIENTO HACIA ADELANTE ---")
    axiomas_actuales = list(base["axiomas"])
    reglas = base["implicaciones"]
    deducciones_cronologicas = []
    
    numero_ciclo = 1
    while True:
        descubrimientos_ciclo = []
        for identificador, regla in reglas.items():
            conclusion = regla["consecuente"]
            condiciones = regla["antecedentes"]
            
            def resolver_cuerpo(premisas_pendientes, mapeo_parcial):
                if not premisas_pendientes:
                    yield mapeo_parcial
                    return
                for hecho_disponible in axiomas_actuales:
                    nuevo_mapeo = unificar_terminos(premisas_pendientes[0], hecho_disponible, mapeo_parcial)
                    if nuevo_mapeo is not None:
                        yield from resolver_cuerpo(premisas_pendientes[1:], nuevo_mapeo)
                        
            for sol_theta in resolver_cuerpo(condiciones, {}):
                fact_derivado = instanciar_literal(conclusion, sol_theta)
                if fact_derivado not in axiomas_actuales and fact_derivado not in descubrimientos_ciclo:
                    descubrimientos_ciclo.append(fact_derivado)
                    
        if not descubrimientos_ciclo:
            break
            
        print(f"Ronda {numero_ciclo} deriva: {descubrimientos_ciclo}")
        deducciones_cronologicas.extend(descubrimientos_ciclo)
        axiomas_actuales.extend(descubrimientos_ciclo)
        numero_ciclo += 1
        
    print(f"Átomos nuevos totales en orden: {deducciones_cronologicas}")
    for item_consulta in lista_consultas:
        es_valido = item_consulta in axiomas_actuales
        print(f"Consulta {item_consulta}: {'PROBADA (Sí)' if es_valido else 'NO PROBADA (No)'}")
    print("\n")

def encadenar_hacia_atras(base, lista_consultas):
    print("--- ENCADENAMIENTO HACIA ATRÁS ---")
    axiomas_validos = base["axiomas"]
    reglas_definidas = base["implicaciones"]
    
    def explorar_objetivo(objetivo, rastro_pila, sangria=""):
        if objetivo in rastro_pila:
            return False
            
        print(f"{sangria}Meta: {objetivo}")
        
        if objetivo in axiomas_validos:
            print(f"{sangria}  -> Es un hecho.")
            return True
            
        for regla_id, definicion in reglas_definidas.items():
            cabeza = definicion["consecuente"]
            theta_match = unificar_terminos(objetivo, cabeza, {})
            if theta_match is not None:
                submetas_resueltas = [instanciar_literal(ant, theta_match) for ant in definicion["antecedentes"]]
                print(f"{sangria}  -> Unifica con {regla_id}. Submetas: {submetas_resueltas}")
                todas_cumplidas = True
                for premisa_req in definicion["antecedentes"]:
                    subobjetivo = instanciar_literal(premisa_req, theta_match)
                    if not explorar_objetivo(subobjetivo, rastro_pila + [objetivo], sangria + "    "):
                        todas_cumplidas = False
                        break
                if todas_cumplidas:
                    return True
        return False

    for item_consulta in lista_consultas:
        print(f"Iniciando consulta: {item_consulta}")
        veredicto = explorar_objetivo(item_consulta, [])
        print(f"Resultado {item_consulta}: {'PROBADA (Sí)' if veredicto else 'NO PROBADA (No)'}\n")

consultas_objetivo = ["AccesoNoche(Ana)", "AccesoNoche(Luis)", "AccesoNoche(Marta)"]
encadenar_hacia_adelante(REGISTRO_BASE, consultas_objetivo)
encadenar_hacia_atras(REGISTRO_BASE, consultas_objetivo)
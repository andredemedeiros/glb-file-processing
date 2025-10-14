import trimesh
import numpy as np
import scipy
import matplotlib.pyplot as plt

from PIL import Image
from pygltflib import GLTF2
from src.data import path_to_glb

def load_glb():
    # Caminho para o seu arquivo .glb
    file_path = path_to_glb

    try:
        # O trimesh carrega o arquivo. Para arquivos glTF/GLB, ele retorna um objeto Scene.
        scene = trimesh.load(file_path)

        # Verifica o tipo de objeto carregado
        if isinstance(scene, trimesh.Scene):
            print("Arquivo .glb carregado com sucesso como uma Cena Trimesh.")
        else:
            # Se o GLB contiver apenas uma malha simples, pode retornar um objeto Trimesh diretamente
            print("Arquivo .glb carregado com sucesso como uma Malha Trimesh.")
        return scene
    
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")


def geometry_data_extract(scene):
    # Se o objeto carregado for uma Cena, obtenha as malhas (geometrias)
    if isinstance(scene, trimesh.Scene):
        # A cena armazena as geometrias em um dicionário
        geometries = list(scene.geometry.values())
    else:
        # Se for apenas uma Malha
        geometries = [scene]

    for i, mesh in enumerate(geometries):
        if isinstance(mesh, trimesh.Trimesh):
            print(f"\n--- Geometria {i+1}: ---")

            # 1. Vértices (Coordenadas X, Y, Z)
            vertices = np.asarray(mesh.vertices)
            print(f"Número de Vértices: {len(vertices)}")
            # print(f"Primeiros 5 Vértices:\n{vertices[:5]}")

            # 2. Faces/Triângulos (Índices dos vértices que formam cada triângulo)
            faces = np.asarray(mesh.faces)
            print(f"Número de Triângulos (Faces): {len(faces)}")
            # print(f"Primeiras 5 Faces:\n{faces[:5]}")

            # 3. Propriedades Calculadas (Bounding Box, Volume, Área)
            print(f"Volume: {mesh.volume:.4f}")
            print(f"Área da Superfície: {mesh.area:.4f}")
            print(f"Limites (Bounding Box):\n{mesh.bounds}")

            # 4. Outras propriedades (Normais)
            normals = np.asarray(mesh.vertex_normals)
            print(f"Número de Normais de Vértice: {len(normals)}")

    
    return geometries

def meta_data_extract():
    #Carrega o arquivo .glb
    file_path = path_to_glb

    gltf_model = GLTF2.load(file_path)

    # 1. Obter o índice da cena principal (índice é um inteiro)
    primary_scene_index = gltf_model.scene

    # 2. Verificar se uma cena principal está definida e se o índice é válido
    if primary_scene_index is not None and 0 <= primary_scene_index < len(gltf_model.scenes):
        
        # Acessa os dados da cena usando o índice
        scene_data = gltf_model.scenes[primary_scene_index]
        
        # Imprime o nome (com tratamento de erro caso o nome não exista)
        scene_name = getattr(scene_data, 'name', 'Sem Nome')
        print(f"Índice da Cena Principal: {primary_scene_index}")
        print(f"Nome da Cena Principal: {scene_name}")
        
        # 3. Se você quiser processar TODOS os nós da cena principal:
        print(f"Nós (Nodes) da Cena Principal (índices): {scene_data.nodes}")

    else:
        print("Nenhuma cena principal padrão definida.")

def raster_xy(geometries):
    # Use a malha da seção anterior (por exemplo, a primeira geometria)
    mesh = geometries[0]

    # --- Projeção Simples (Vista Lateral) ---
    # O `scene.show()` renderiza a cena e retorna uma imagem rasterizada (np.array)
    # Nota: Para renderizar, 'trimesh' geralmente precisa do pacote 'pyrender' ou 'open3d'
    # Se a instalação for complicada, você pode usar a funcionalidade de projeção que não precisa do renderizador 3D:

    # Crie um objeto Scene a partir da Malha
    scene = mesh.scene()

    # 1. Projeção Ortopédica (Top-down view - Vista de Cima)
    # Para uma vista de cima, a câmera olha para baixo no eixo Z.
    transform_z = np.array([
        [1, 0, 0, 0],
        [0, 0, -1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ])
    scene.apply_transform(transform_z)
    # Nota: O uso de renderização 2D/3D em Python pode exigir configurações adicionais
    # de bibliotecas (como pyrender, pyglet, etc.) que dependem do sistema operacional.
    # O método mais universal é usar a projeção dos pontos:

    # Projeção no plano XY (Vista de Cima)
    vertices_xy = mesh.vertices[:, :2] # Pegue apenas as coordenadas X e Y
    faces_triangles = mesh.faces

    plt.figure(figsize=(8, 8))
    plt.title(f"Vista de Cima (Projeção XY) do Objeto")
    plt.xlabel("Eixo X")
    plt.ylabel("Eixo Y")

    # Desenha as bordas da malha (wireframe)
    plt.triplot(vertices_xy[:, 0], vertices_xy[:, 1], faces_triangles, color='gray', linewidth=0.5, alpha=0.5)

    # Desenha os vértices
    plt.plot(vertices_xy[:, 0], vertices_xy[:, 1], 'o', markersize=2, color='blue')

    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

    return mesh,scene

def raster_xy_with_depth_color(geometries):
    # Use a malha da seção anterior (por exemplo, a primeira geometria)
    mesh = geometries[0]

    # --- 1. PREPARAÇÃO DOS DADOS ---
    # Coordenadas X e Y (para a posição no gráfico 2D)
    vertices_xy = mesh.vertices[:, :2] 
    
    # Coordenadas Z (para o valor de cor)
    # Z representa a altura/profundidade na projeção XY (Vista de Cima)
    depth_values = mesh.vertices[:, 2] 

    # Acesso seguro ao nome da malha para o título
    mesh_name = mesh.metadata.get('name', 'Sem Nome')

    # --- 2. CONFIGURAÇÃO DO GRÁFICO ---
    plt.figure(figsize=(10, 10))
    plt.title(f"Vista de Cima (Projeção XY) do Objeto: {mesh_name}\nCor = Profundidade/Altura (Eixo Z)")
    plt.xlabel("Eixo X")
    plt.ylabel("Eixo Y")

    # --- 3. PLOTAGEM COM DISPERSÃO E MAPA DE CORES ---
    # Usamos scatter para colorir cada ponto (vértice) individualmente
    # c=depth_values: define o valor de cor (Z)
    # cmap='viridis': o mapa de cores a ser usado (pode ser 'jet', 'plasma', etc.)
    scatter = plt.scatter(
        vertices_xy[:, 0], 
        vertices_xy[:, 1], 
        c=depth_values,          # Use o eixo Z para a cor
        cmap='viridis',          # Mapa de cores para representar a profundidade
        s=5,                     # Tamanho do ponto (ajuste conforme necessário)
        marker='.',
        alpha=1.0                # Opacidade
    )

    # --- 4. BARRA DE CORES (LEGENDA) ---
    # Adiciona a barra de cores para mostrar a correspondência entre cor e valor Z
    cbar = plt.colorbar(scatter)
    cbar.set_label('Coordenada Z (Profundidade/Altura)')

    # --- 5. AJUSTE DE ESCALA ---
    min_x, min_y = mesh.bounds[0, :2]
    max_x, max_y = mesh.bounds[1, :2]
    range_val = max(max_x - min_x, max_y - min_y)
    margin = 0.05 * range_val
    
    plt.xlim(min_x - margin, max_x + margin)
    plt.ylim(min_y - margin, max_y + margin)
    
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

    # Retorna a malha e a cena (conforme a função original)
    return mesh, mesh.scene()


def slice_z(mesh):
    # Exemplo de Secção (Corte)
    # Origem do plano de corte (no centro do bounding box)
    plane_origin = mesh.centroid

    # Normal do plano (corte na horizontal, perpendicular ao eixo Z)
    plane_normal = [0, 0, 1]

    # Crie a seção transversal
    section = mesh.section(plane_origin=plane_origin, plane_normal=plane_normal)

    if section:
        # A seção é uma coleção de caminhos
        paths = section.entities
        
        plt.figure(figsize=(6, 6))
        plt.title(f"Secção Transversal (Corte Horizontal) em Z={plane_origin[2]:.2f}")
        plt.xlabel("Eixo X")
        plt.ylabel("Eixo Y")

        # Desenha os caminhos 2D
        for path in paths:
            if hasattr(path, 'vertices'):
                # Desenha as curvas de contorno
                plt.plot(path.vertices[:, 0], path.vertices[:, 1], color='red', linewidth=2)
                
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
    else:
        print("Nenhuma seção transversal encontrada no centro.")

    # Calcule os limites do modelo no eixo Z
    min_z = mesh.bounds[0, 2]
    max_z = mesh.bounds[1, 2]

    # Defina um número de fatias (ex: 10 fatias)
    num_slices = 100
    slices_z = np.linspace(min_z, max_z, num_slices + 2)[1:-1] # Ignora as bordas extrema

    plt.figure(figsize=(8, 8))
    plt.title("Múltiplas Secções Transversais")
    plt.xlabel("Eixo X")
    plt.ylabel("Eixo Y")

    found_section = False
    for z in slices_z:
        plane_origin = [mesh.centroid[0], mesh.centroid[1], z] # Mantém X e Y do centroide, varia Z
        plane_normal = [0, 0, 1]

        section = mesh.section(plane_origin=plane_origin, plane_normal=plane_normal)

        if section:
            found_section = True
            paths = section.entities

            print(f"Secção encontrada em Z={z:.4f}. Total de caminhos: {len(paths)}") # <--- LINHA DE DEBBUG

            for path in paths:
                if hasattr(path, 'vertices'):
                    # Desenha as curvas de contorno com cores diferentes
                    #plt.plot(path.vertices[:, 0], path.vertices[:, 1], linewidth=1.5, alpha=0.7)
                    plt.plot(path.vertices[:, 0], path.vertices[:, 1], linewidth=3, alpha=1.0, color='blue') 


    plt.gca().set_aspect('equal', adjustable='box')

    if found_section:
        # --- AJUSTE DE ESCALA (Bounds) ---
        # mesh.bounds[0, :2] são as coordenadas [min_x, min_y]
        # mesh.bounds[1, :2] são as coordenadas [max_x, max_y]
        min_x, min_y = mesh.bounds[0, :2]
        max_x, max_y = mesh.bounds[1, :2]
        
        # Adiciona uma margem de 10% (0.1) do tamanho total da malha
        range_x = max_x - min_x
        range_y = max_y - min_y
        margin = 0.1 * max(range_x, range_y)
        
        plt.xlim(min_x - margin, max_x + margin) # Define o limite X
        plt.ylim(min_y - margin, max_y + margin) # Define o limite Y
        
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()

    else:
        # Se ainda assim não encontrar nada, a malha pode estar muito danificada ou ser apenas um ponto.
        print("Ainda não foi possível encontrar seções transversais. Verifique a integridade do modelo.")

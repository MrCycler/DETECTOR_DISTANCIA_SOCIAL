import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from IPython.display import clear_output
import pandas as pd

def TransformPoints(in_points,T_Matrix):
    """Esta función transforma puntos de la imagen original en puntos de la imagen en bird-eye
    Arguments:
        in_points, T_Matrix
    Returns:
        out_points
    """
    #Aplicacion de la transformación
    if in_points !=[]:
        puntos_np = np.array([in_points], dtype=np.float32)
        out_points = cv2.perspectiveTransform(puntos_np,np.array(T_Matrix))
    else:
        return []
    return out_points[0]

def PolicyPoints(in_points,window_points,threshold):
    """Recibe coordenadas de puntos trasnsformados de la segunda imagen, así como los puntos que determinan los boundingboxes 
    de la primera imagen y en base a un threshold de distancia dado en cm establece si los puntos o los bounding boxes cumplen
    con la distancia requerida. Además da las coordenadas de una recta que relaciona los puntos que no cumplen con la regla.
    Arguments:
        in_points,window_points,threshold
    Returns:
        window_buenos,window_malos,buenos,malos,lines_points
    """
    buenos = []
    malos = []
    window_buenos = []
    window_malos = []
    lines_points = []
    point2_temp = []
    pix_unit = 1.7
    i = 0
    for point in in_points:
        es_malo = False
        for point2 in in_points:
            distance = math.sqrt((point[0]-point2[0])*(point[0]-point2[0])+(point[1]-point2[1])*(point[1]-point2[1]))
            if 0<distance < (threshold*pix_unit):
                es_malo = True
                point2_temp = point2
                break
        if es_malo ==False:
            buenos.append(point)
            window_buenos.append(window_points[i])
            i = i + 1
        else:
            malos.append(point)
            window_malos.append(window_points[i])
            lines_points.append([point,point2_temp])
            i = i + 1
    return window_buenos,window_malos,buenos,malos,lines_points

def ViewTransformPoints(buenos, malos,lines_points,final_size):
    """ Genera la imagen desde bird-eye dibujando los puntos que representan a las personas marcando con color verde los
    que cumplen con la distancia y en color rojo los que no, recibe las dimensiones de la imagen
    Arguments:
        buenos, malos,lines_points,height_img,width_img
    Returns:
        frame_rgb - imagen de salida
    """
    (width_img,height_img) = final_size
    blank_image = np.zeros((height_img,width_img ,3), np.uint8)
    # se dibujan los puntos en la imagen de ojo de halcon
    for point in buenos:
        cv2.circle(blank_image,tuple(point), 30, (0,255,0), -1)
    for point in malos:
        cv2.circle(blank_image,tuple(point), 30, (0,0,255), -1)
    for par in lines_points:
        line_thickness = 2
        blank_image = cv2.line(blank_image,tuple(par[0]), tuple(par[1]), (0, 0, 255), thickness=line_thickness)
    b,g,r = cv2.split(blank_image)
    frame_rgb = cv2.merge((r,g,b))
    frame_rgb= frame_rgb[0:3500,2000:4200]
    return frame_rgb

def detector10(path,let_distance,df,final_size,T_Matrix): 
    """Una versión reducida del detector que se aplica a los primeros 10 frames
    Arguments:
        path - ruta del video
        let_distance - distancia permitida en cm
        df - frame de datos con
        final_size - tamaño final de la imagen de salida
        T_Matrix - matrix de transformación de imagen original a ojo de halcon
    """
    vidObj = cv2.VideoCapture(path) 
    count = 0
    success = 1
    while success and count<10: 
        success, image = vidObj.read() 
        filter_df = df[df['Frame']==(count+1)]
        # Se obtienen los puntos que corresponden a las cabezas
        head_points = []
        window_points = []
        for index,row in filter_df.iterrows():
            start_point = (int(float(row['headLeft'])), int(float(row['headTop'])) )
            end_point = (int(float(row['headRight'])), int(float(row['headBottom'])))
            start_point2 = (int(float(row['bodyLeft'])), int(float(row['bodyTop'])) )
            end_point2 = (int(float(row['bodyRight'])), int(float(row['bodyBottom']))) 
            window_points.append([start_point,end_point,start_point2,end_point2])
            head_point = (int(start_point[0]/2+end_point[0]/2),int(start_point[1]/2+end_point[1]/2))
            head_points.append(head_point)
        head_transform_points=TransformPoints(np.array(head_points),T_Matrix)
        w_buenos,w_malos,buenos, malos, lines_points = PolicyPoints(head_transform_points,window_points,let_distance*100)
        for ventana in w_buenos:
            thickness = 2
            image = cv2.rectangle(image, ventana[0], ventana[1], (0,255,0), thickness) 
            image = cv2.rectangle(image, ventana[2], ventana[3], (0,255,0), thickness) 
        for ventana in w_malos:
            thickness = 2
            image = cv2.rectangle(image, ventana[0], ventana[1], (0,0,255), thickness) 
            image = cv2.rectangle(image, ventana[2], ventana[3], (0,0,255), thickness)   
        falcon_image=ViewTransformPoints(buenos,malos,lines_points,final_size)
        plt.figure(figsize = (20,8))
        plt.subplot(121)
        plt.title('Original') 
        b,g,r = cv2.split(image)
        frame_rgb = cv2.merge((r,g,b))
        plt.imshow(frame_rgb)
        plt.subplot(122)
        plt.imshow(falcon_image)
        plt.title('Ojo de halcon') 
        plt.show()
        clear_output(wait=True)
        count += 1

def detector(path,let_distance,df,final_size,T_Matrix): 
    """Una versión reducida del detector que se aplica a los primeros 10 frames
    Arguments:
        path - ruta del video
        let_distance - distancia permitida en cm
        df - frame de datos con
        final_size - tamaño final de la imagen de salida
        T_Matrix - matrix de transformación de imagen original a ojo de halcon
    """
    vidObj = cv2.VideoCapture(path) 
    count = 0
    success = 1
    while success: 
        success, image = vidObj.read() 
        filter_df = df[df['Frame']==(count+1)]
        # Se obtienen los puntos que corresponden a las cabezas
        head_points = []
        window_points = []
        for index,row in filter_df.iterrows():
            start_point = (int(float(row['headLeft'])), int(float(row['headTop'])) )
            end_point = (int(float(row['headRight'])), int(float(row['headBottom'])))
            start_point2 = (int(float(row['bodyLeft'])), int(float(row['bodyTop'])) )
            end_point2 = (int(float(row['bodyRight'])), int(float(row['bodyBottom']))) 
            window_points.append([start_point,end_point,start_point2,end_point2])
            head_point = (int(start_point[0]/2+end_point[0]/2),int(start_point[1]/2+end_point[1]/2))
            head_points.append(head_point)
        head_transform_points=TransformPoints(np.array(head_points),T_Matrix)
        w_buenos,w_malos,buenos, malos, lines_points = PolicyPoints(head_transform_points,window_points,let_distance*100)
        for ventana in w_buenos:
            thickness = 2
            image = cv2.rectangle(image, ventana[0], ventana[1], (0,255,0), thickness) 
            image = cv2.rectangle(image, ventana[2], ventana[3], (0,255,0), thickness) 
        for ventana in w_malos:
            thickness = 2
            image = cv2.rectangle(image, ventana[0], ventana[1], (0,0,255), thickness) 
            image = cv2.rectangle(image, ventana[2], ventana[3], (0,0,255), thickness)   
        falcon_image=ViewTransformPoints(buenos,malos,lines_points,final_size)
        plt.figure(figsize = (20,8))
        plt.subplot(121)
        plt.title('Original') 
        b,g,r = cv2.split(image)
        frame_rgb = cv2.merge((r,g,b))
        plt.imshow(frame_rgb)
        plt.subplot(122)
        plt.imshow(falcon_image)
        plt.title('Ojo de halcon') 
        plt.show()
        clear_output(wait=True)
        count += 1

def transformation_matrix():
    """Retorna la matriz de transformación generada en los experimentos
    Arguments:
        None
    Returns:
        T_matrix
    """
    return [[ 1.43809441e+00 , 7.58290450e+00  ,7.93117275e+02],
            [-6.80696958e-01 , 8.22103159e+00  ,1.35956100e+03],
             [-7.73887614e-06  ,1.76518761e-03  ,1.00000000e+00]]

def final_size():
    """Retorna las dimensiones que tendrá la imagen resultado
    Arguments:
        None
    Returns:
        final_size=(width_img,height_img)
    """
    width_img = 5000
    height_img = 3500
    #Dimensiones de la imagen final
    final_size=(width_img,height_img)
    return final_size 
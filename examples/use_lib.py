import dfs
from dfs import core                                                       
from dfs import dfs                                                       

def demonstrate_usage():
    print("--- Début de la démonstration de dfs ---")
                                     
    print("\n[Exemple 1 : Appel d'une fonction de dfs.core]")
    try:             
        input_data_1 = "Données d'entrée pour core"
        parametre_1 = {"option": True, "valeur": 123}
        
        resultat_core = core.example_core_function(input_data_1, config=parametre_1)
        
        print(f"  Fonction: core.example_core_function")
        print(f"  Entrée: '{input_data_1}', Config: {parametre_1}")
        print(f"  Résultat: {resultat_core}")
        
    except AttributeError:
        print("  ERREUR: La fonction 'example_core_function' n'existe pas dans dfs.core.")
        print("  Veuillez adapter cet exemple avec les vrais noms de votre librairie.")
    except Exception as e:
        print(f"  Une erreur inattendue est survenue dans l'Exemple 1: {e}")
                                                           
    print("\n[Exemple 2 : Instanciation et utilisation d'une classe de dfs.core]")
    try:                                                        
        instance = core.ExampleCoreClass()                                     
        print(f"  Classe: core.ExampleCoreClass")
        print(f"  Instance créée: {instance}")
             
        input_data_2 = [10, 20, 30]
        resultat_methode = instance.example_method(data=input_data_2)
        
        print(f"  Méthode appelée: example_method")
        print(f"  Entrée méthode: {input_data_2}")
        print(f"  Résultat méthode: {resultat_methode}")

    except AttributeError:
        print("  ERREUR: La classe 'ExampleCoreClass' ou la méthode 'example_method' n'existe pas.")
        print("  Veuillez adapter cet exemple avec les vrais noms de votre librairie.")
    except Exception as e:
        print(f"  Une erreur inattendue est survenue dans l'Exemple 2: {e}")
                                  
    print("\n[Exemple 3 : Appel d'une fonction de dfs.dfs]")
    try:                  
        input_data_3 = 5.5
        resultat_dfs = dfs.example_dfs_function(input_data_3)

        print(f"  Fonction: dfs.example_dfs_function")
        print(f"  Entrée: {input_data_3}")
        print(f"  Résultat: {resultat_dfs}")

    except AttributeError:
        print("  ERREUR: La fonction 'example_dfs_function' n'existe pas dans dfs.dfs.")
        print("  Veuillez adapter cet exemple avec les vrais noms de votre librairie.")
    except Exception as e:
        print(f"  Une erreur inattendue est survenue dans l'Exemple 3: {e}")

    print("\n[Exemple 4 : Accéder à __version__ (si défini dans dfs/__init__.py)]")
    try:                                           
        version = dfs.__version__
        print(f"  Version de dfs installée : {version}")
    except AttributeError:
        print("  L'attribut '__version__' n'est pas défini dans dfs/__init__.py.")
        
    print("\n--- Fin de la démonstration ---")


if __name__ == "__main__":
    demonstrate_usage()

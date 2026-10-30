import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import random
import csv


#constatntes de la grille:
maxX=5
maxY=5
ZONE_COUNT=4
DANGER ={(1,4),(4,4),(2,1),(5,1)}

#etat initial en forme de dictionnaire :
def make_initial_state():
    state = {
        "posX": 0,
        "posY": 0,
        "baseX": 0,
        "baseY": 0,
        "battery": 100,
        "obstacle_distance": 2,
        "docked": 0,
        "airborne": 0,
        "crashed": 0,
        "visZones": set(),
    }
    state["visZones"].add(zoneof(state["posX"], state["posY"]))
    return state
#retourne lazone de x et y:
def zoneof(X , Y):
    if(X <= maxX/2 and Y<= maxY/2):
        return 1
    elif (X <= maxX/2 and Y>maxY/2):
        return 2
    elif (X > maxX/2 and Y<= maxY/2):
        return 3
    else :
        return 4
#retourne vrai si la zone est dans les zones dangereuses:
def is_danger(x,y):
    return (x,y)in DANGER
#mise ajour la distance par rappoert a lobstacle:
def update_obstacle_distance(state,x,y):
    if is_danger(x,y):
        state["obstacle_distance"]=0
    else:
         state["obstacle_distance"]=2

#voisins valides

def get_neighbors(x,y):
    neighbors=[]
    if y<maxY:
        neighbors.append((x,y+1))
    if x<maxX:
        neighbors.append((x+1,y))
    if y>0:
        neighbors.append((x,y-1))
    if x>0:
        neighbors.append((x-1,y))
    return neighbors
#on verifie la coherence de toutes les contraintes a chaque operation (possible ou pas)
def check_invariant(state):
    assert 0 <= state["posX"] <= maxX
    assert 0 <= state["posY"] <= maxY
    assert 0 <= state["baseX"] <= maxX
    assert 0 <= state["baseY"] <= maxY
    assert 0 <= state["battery"] <= 100
    assert state["docked"] in (0, 1)
    assert state["airborne"] in (0, 1)
    assert state["crashed"] in (0, 1)
    assert state["visZones"].issubset(set(range(1, ZONE_COUNT + 1)))
    if state["crashed"] == 1:
        assert state["airborne"] == 0
    if state["docked"] == 1:
        assert state["airborne"] == 0
        assert state["posX"] == state["baseX"]
        assert state["posY"] == state["baseY"]
#affichage////////////////////////////////(avec laide de lia )
ZONE_COLORS   = ["#cfe8ff", "#fff3bf", "#d3f9d8", "#ffe0cc"]
ZONE_LABEL_POS = {1: (1.0, 1.0), 2: (1.0, 3.5), 3: (3.5, 1.0), 4: (3.5, 3.5)}
 
def draw_grid(ax, state, title=""):
    ax.clear()
    N_x = maxX + 1
    N_y = maxY + 1
 
    # fond coloré par zone
    zone_map = np.zeros((N_x, N_y), dtype=int)
    for x in range(N_x):
        for y in range(N_y):
            zone_map[x, y] = zoneof(x, y)
    cmap = ListedColormap(ZONE_COLORS)
    ax.imshow(zone_map.T, cmap=cmap, origin="lower", vmin=1, vmax=4, aspect="equal")
 
    # grille
    ax.set_xticks(np.arange(-0.5, N_x, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, N_y, 1), minor=True)
    ax.grid(which="minor", color="#888", linewidth=1)
    ax.set_xticks(range(N_x))
    ax.set_yticks(range(N_y))
    ax.tick_params(which="both", bottom=False, left=False,
                   labelbottom=True, labelleft=True)
 
    # labels de zones (vert = visitée, gris = non visitée)
    for z, (cx, cy) in ZONE_LABEL_POS.items():
        visited = z in state["visZones"]
        ax.text(cx, cy, f"Zone {z}",
                ha="center", va="center", fontsize=9,
                color="#27ae60" if visited else "#aaa",
                fontweight="bold" if visited else "normal")
 
    # cellules dangereuses
    for (ox, oy) in DANGER:
        ax.add_patch(plt.Rectangle((ox - 0.5, oy - 0.5), 1, 1,color="red", alpha=0.25, zorder=1))
        ax.text(ox, oy, "✖", ha="center", va="center",fontsize=14, color="red", zorder=2)
 
    # base
    bx, by = state["baseX"], state["baseY"]
    ax.add_patch(plt.Rectangle((bx - 0.5, by - 0.5), 1, 1,color="blue", alpha=0.15, zorder=1))
    ax.text(bx, by, "B", ha="center", va="center",fontsize=16, fontweight="bold", color="blue", zorder=3)
 
    # drone
    px, py = state["posX"], state["posY"]
    if state["crashed"]:
        symbol, color = "BOOM", "red"
    elif state["airborne"]:
        symbol, color = "▲", "black"
    elif state["docked"]:
        symbol, color = "D", "blue"
    else:
        symbol, color = "●", "gray"
    ax.text(px, py, symbol, ha="center", va="center",
            fontsize=20, color=color, zorder=4)
 
    # barre de batterie en bas
    bat = state["battery"]
    bat_color = "#2ecc71" if bat > 50 else ("#f39c12" if bat > 20 else "#e74c3c")
    # fond gris
    ax.add_patch(plt.Rectangle((-0.5, -1.1), maxX + 1, 0.4, color="#ddd", zorder=1, clip_on=False))
    # barre colorée
    ax.add_patch(plt.Rectangle((-0.5, -1.1), (maxX + 1) * bat / 100, 0.4,color=bat_color, zorder=2, clip_on=False))
    ax.text(maxX / 2, -0.9, f"Batterie : {bat}%",ha="center", va="center", fontsize=8, zorder=3, clip_on=False)
 
    # statut drone
    if state["crashed"]:    statut = " CRASH"
    elif state["airborne"]: statut = "✈ EN VOL"
    elif state["docked"]:   statut = "D ARRIMÉ"
    else:                   statut = "● AU SOL"
 
    ax.text(maxX / 2, -1.55,
            f"{statut}  |  Zones visitées : {sorted(state['visZones'])}  |  "
            f"obs_dist={state['obstacle_distance']}",
            ha="center", va="center", fontsize=8, clip_on=False)
 
    ax.set_xlim(-0.6, maxX + 0.5)
    ax.set_ylim(-1.8, maxY + 0.5)
    ax.set_title(title or "Drone de patrouille", fontsize=10, pad=6)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
 
def init_figure():
    plt.ion()
    fig, ax = plt.subplots(figsize=(7, 8))
    fig.subplots_adjust(bottom=0.05)
    return fig, ax
 
def refresh(fig, ax, state, title=""):
    draw_grid(ax, state, title)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.1)
 

#operations:
def takeoff_cmd(state,silent=False):
    if not (state["crashed"] == 0 and state["airborne"] == 0 and state["docked"] == 0 and state["battery"] > 0):
        if not silent: 
            print("[undock_cmd] Précondition non satisfaite.")
            print("[takeoff_cmd] Précondition non satisfaite.")
        return False
    state["airborne"] = 1
    update_obstacle_distance(state, state["posX"], state["posY"])
    check_invariant(state)
    return True


def move_step(state,silent=False):
    if not(state["crashed"] == 0 and state["airborne"] == 1 and state["docked"] == 0 and state["battery"] > 0):
        if not silent: 
            print("[undock_cmd] Précondition non satisfaite.")
            print("[move_step] Précondition non satisfaite.")
        return False
    neighbors=get_neighbors(state["posX"],state["posY"])
    next_x,next_y=random.choice(neighbors)
    state["posX"]=next_x
    state["posY"]=next_y
    state["battery"] -=1
    state["visZones"].add(zoneof(next_x,next_y))
    update_obstacle_distance(state,next_x,next_y)
    check_invariant(state)
    return True


def avoid_maneuver(state,silent=False):
    if not(state["crashed"] == 0 and state["airborne"] == 1 and state["docked"] == 0 and state["battery"] > 1):
        if not silent: 
            print("[undock_cmd] Précondition non satisfaite.")
            print("[avoid_maneuver] Précondition non satisfaite.")
        return False
    neighbors =get_neighbors(state["posX"],state["posY"])
    safe =[(x,y) for (x,y)in neighbors if not is_danger(x,y)]
    if len(safe)>0:
        next_x,next_y=random.choice(safe) #on choisit d'un voisin safe
        state["posX"]=next_x
        state["posY"]=next_y
        state["battery"] -=2
        state["visZones"].add(zoneof(next_x,next_y))
        state["obstacle_distance"]=2
    else:
        next_x,next_y=random.choice(neighbors)
        state["posX"]=next_x
        state["posY"]=next_y
        state["battery"] -=2
        state["visZones"].add(zoneof(next_x,next_y))
        update_obstacle_distance(state,next_x,next_y)
    check_invariant(state)
    return True

def return_home(state,silent=False):
    if not (state["crashed"]==0 and state ["airborne"]==1 and state["docked"]==0 and state ["battery"]>0):
        if not silent: 
            print("[undock_cmd] Précondition non satisfaite.")
            print("returning home is not possible ")
        return False
    if state["posX"]<state["baseX"]:
        next_x=state["posX"]+1
    elif state["posX"]>state["baseX"]:
        next_x=state["posX"]-1
    else:
        next_x=state["posX"]

    if state["posY"]<state["baseY"]:
        next_y=state["posY"]+1
    elif state["posY"]>state["baseY"]:
        next_y=state["posY"]-1
    else:
        next_y=state["posY"]
    state["battery"]-=1
    state["posX"]=next_x
    state["posY"]=next_y
    state["visZones"].add(zoneof(next_x,next_y))
    update_obstacle_distance(state,next_x,next_y)
    check_invariant(state)
    return True

def dock_cmd(state,silent=False):
     if not (state["crashed"]==0 and state ["airborne"]==1 and state["posX"]==state["baseX"]and  state["posY"]==state["baseY"]):
        if not silent: 
            print("[dock_cmd] Précondition non satisfaite.")
            print("charging not possible ")
        return False
     state["docked"]=1
     state ["airborne"]=0
     check_invariant(state)
     return True

def undock_cmd(state,silent=False):
     if not (state["crashed"]==0 and state ["docked"]==1 and state["battery"]>0):
        if not silent:
            print("[undock_cmd] Précondition non satisfaite.")
            print("uncharging not possible ")
        return False
     state["docked"]=0
     state ["airborne"]=1
     check_invariant(state)
     return True

def charge_step(state,silent=False):
    if not (state["crashed"]==0 and state ["docked"]==1 ):
        if not silent: 
            print("[undock_cmd] Précondition non satisfaite.")
            print("charging  step not possible ")
        return False
    if state["battery"]<=95:
        state["battery"]+=5
    else:
        state["battery"]=100
    check_invariant(state)
    return True
 
def emergency_stop (state,silent=False):
    state["crashed"]=1
    state ["airborne"]=0
    state ["docked"]=0
    state["obstacle_distance"]=0
    check_invariant(state)
    return True
 

 


        
#affichage( )
def render(state):
    N_x=maxX +1
    N_y=maxY +1
    zone_map=np.zeros((N_x,N_y),dtype=int)
    for x in range(N_x):
        for y in range(N_y):
            zone_map[x,y]=zoneof(x,y)
    fig ,ax=plt.subplots(figsize=(N_y +1,N_x +1 ))
    cmap=ListedColormap(["#cfe8ff", "#fff3bf", "#d3f9d8", "#ffe0cc"])
    ax.imshow(zone_map.T, cmap=cmap, origin="lower", vmin=1, vmax=4)
    ax.set_xticks(np.arange(-0.5, N_x, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, N_y, 1), minor=True)
    ax.grid(which="minor", color="gray", linewidth=1)
    ax.tick_params(which="both", bottom=False, left=False,
                   labelbottom=True, labelleft=True)
    ax.set_xticks(range(N_x))
    ax.set_yticks(range(N_y))
 
 #obstacles
    for (ox,oy) in DANGER:
        if 0<=oy<= maxY and 0<=ox<= maxX:
            ax.text(ox,oy,"x", ha="center",va="center",fontsize=16,color="red")
#base
    ax.text(state["baseX"], state["baseY"], "B", ha="center", va="center",
            fontsize=16, fontweight="bold", color="blue")

#drone
    symbol ="BOOM" if state ["crashed"] else ("D" if state ["airborne"] else "d")
    ax.text(state["posX"],state["posY"],symbol,ha="center",va="center",
             fontsize=16, fontweight="bold", color="black")
#legende etat 
    info = (f"battery={state['battery']}  airborne={state['airborne']}  "
            f"docked={state['docked']}  crashed={state['crashed']}  "
            f"obs_dist={state['obstacle_distance']}  "
            f"zones={sorted(state['visZones'])}")
    ax.set_title(info, fontsize=9)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    plt.tight_layout()
    plt.show()


#MODE INTERACTIF ///////////////////////////////////////////////////////
ACTIONS={
    "takeoff":takeoff_cmd,
    "move":move_step,
    "avoid":avoid_maneuver,
    "home":return_home,
    "dock": dock_cmd,
    "undock": undock_cmd,
    "charge":charge_step,
    "emergency": emergency_stop,

}

def mode_interactif():
    state=make_initial_state()
    fig, ax = init_figure()
    refresh(fig, ax, state, "État initial")

    print("mode interactif !")
    print("les actions disponibles:", ", ".join(ACTIONS.keys()))
    print("taper q pour quitter , G pour afficher la grille ")
    while True:
        print(f"État : pos=({state['posX']},{state['posY']}) "
              f"bat={state['battery']} air={state['airborne']} "
              f"dock={state['docked']} crash={state['crashed']} "
              f"zones={sorted(state['visZones'])}")
        if state["crashed"]:
            print ("BOOM ... Drone craché , Fin de la mission ")
            break 
        cmd=input("Action >").strip().lower()
        if cmd == "q":
            break
        if cmd == "G":
            render(state)
        elif cmd in ACTIONS :
            ok=ACTIONS[cmd](state)
            if  ok:
                refresh(fig, ax, state, f"Dernière action : {cmd}")
            else:
                print("  → Action refusée.")

        else:
            print("action inconnue !")
    plt.ioff()
    plt.show()

        
#MODE AUTOMATIQUE //////////////////////////////////////////////////////////////

def mode_automatique(fichier_csv):
    state=make_initial_state() #creer l'etat initial
    fig, ax = init_figure() #ouverture de la fenetre graphique
    refresh(fig, ax, state, "État initial")

    print("MODE AUTOMATIQUE")
    try:
        with open(fichier_csv,newline="")as f: #on ouvre le fichier csv
            reader=csv.reader(f)
            for i,row in enumerate(reader): #lire le fichier ligne par ligne 
                if not row: # si ligne vide on passe 
                    continue
                cmd=row[0].strip().lower()# recuperation de la commande 
                print(f"etape{i+1}:{cmd}")
                if state["crashed"]:
                    print("drone crashé")
                    break
                if cmd not in ACTIONS:# commande non reconnue 
                    print (f" action inconnue")
                    break
                ok=ACTIONS[cmd](state) #on l'execute
                #affichage grille
                titre = f"Étape {i+1} : {cmd}" + ("" if ok else " (refusée)")
                print(f"  {titre} | pos=({state['posX']},{state['posY']}) bat={state['battery']}")
                #mise a jour de la grille
                refresh(fig, ax, state, titre)
                if not ok:
                    break
                if state["crashed"]:
                    refresh(fig, ax, state, " CRASH")
                    break
    except FileNotFoundError:
        print(f"Fichier '{fichier_csv}' introuvable.")
 
    plt.ioff()#affichage de la fenetre 
    plt.show()
 




# MODE EXHAUSTIF ///////////////////////////////////////////////////////////////
def state_to_key(state):  #fontion pour convertir etat en tuple hashable
    return(     state["posX"], state["posY"],
        state["baseX"], state["baseY"],
        state["battery"],
        state["obstacle_distance"],
        state["docked"],
        state["airborne"],
        state["crashed"],
        frozenset(state["visZones"]),)
def copy_state(state):
    s=dict(state)
    s["visZones"]=set(state["visZones"])
    return s

def mode_exhaustif(maxDepth=-1, maxBreadth=-1):
    print("=== MODE EXHAUSTIF ===")
    visited =set() #ensemble d'etats deja visités
    states_map ={} #key state pour garder les etats complets
    transitions={} #key lisye de (action,next_key)
 
    def get_all_successors(state):#genere tous les etats suivants possibles
        result=[]
        for fn,name in [
            (takeoff_cmd,"takeoff"),
            (dock_cmd,"dock"),
            (undock_cmd, "undock"),
            (charge_step,"charge"),
            (emergency_stop,"emergency")
        ]:
            s=copy_state(state) #on copie loriginal pour ne pas le perdre 
            if fn (s,silent=True):
                result.append((name,s))
        if (state["crashed"]==0 and state["airborne"]==1 and state ["docked"]==0 and state ["battery"]>0):
            s=copy_state(state)
            if return_home(s,silent=True):
                result.append(("home",s))
        if (state["crashed"]==0 and state["airborne"]==1 and state["docked"]==0 and state["battery"]>0):
            for (nx, ny) in get_neighbors(state["posX"], state["posY"]):
                s = copy_state(state)
                s["posX"]=nx; s["posY"]=ny; s["battery"]-=1
                s["visZones"].add(zoneof(nx, ny))
                update_obstacle_distance(s, nx, ny)
                result.append(("move", s))
        #4 sucesseurs possible : action non deterministe
        if (state["crashed"]==0 and state["airborne"]==1
                and state["docked"]==0 and state["battery"]>1):
            neighbors = get_neighbors(state["posX"], state["posY"])
            safe = [(x,y) for (x,y) in neighbors if not is_danger(x,y)]
            targets = safe if safe else neighbors
            for (nx, ny) in targets:
                s = copy_state(state)
                s["posX"]=nx; s["posY"]=ny; s["battery"]-=2
                s["visZones"].add(zoneof(nx, ny))
                s["obstacle_distance"] = 2 if safe else (0 if is_danger(nx,ny) else 2)
                result.append(("avoid", s))
        return result

            
    def explore(state,depth,breadth):
        key=state_to_key(state)
        if key in visited: # si deja visité on fait rien
            return
        visited.add(key) # on lajoute a la liste de zones visités 
        states_map[key]=state
        transitions[key]=[]
        if depth !=-1 and depth <=0: # limite de profondeur atteinte
            return
        if state ["crashed"]:# drone crashé on s'arrete
            return
        count =0
        for (action_name, next_state) in get_all_successors(state): # on axplore tous les successeurs
            if breadth != -1 and count >= breadth:
                break                
            try:
                    check_invariant(next_state)
            except AssertionError:
                continue
            next_key = state_to_key(next_state)
            transitions[key].append((action_name, next_key))
            next_depth = -1 if depth == -1 else depth - 1
            explore(next_state, next_depth, breadth)
            count += 1
    
    import sys 
    #on augmente la limite de recursion python
    sys.setrecursionlimit(100000)
    #on lance lexploration depuis l'etat initial 
    explore(make_initial_state(), maxDepth, maxBreadth)
    #calcul des stat
    n_etats       = len(visited) #nombre d'etats couverts
    n_transitions = sum(len(v) for v in transitions.values())#nombre total de transitions
    crashed_states = [s for s in states_map.values() if s["crashed"] == 1] #les etats ou le drone a crashé
    max_zones     = max(len(s["visZones"]) for s in states_map.values()) #zone couvertes
    best_states   = [s for s in states_map.values() if len(s["visZones"]) == max_zones] #les etats qui ont couvert toutes les zones 
    #affichage
    print(f"\nExploration terminée :")
    print(f"  {n_etats} états explorés")
    print(f"  {n_transitions} transitions")
    print(f"  {len(crashed_states)} états crash")
    print(f"  Couverture max : {max_zones}/{ZONE_COUNT} zones")
    
    #affichage graphique (a laide de l'ia )

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle(
        f"Exploration exhaustive (depth-first)\n"
        f"{n_etats} états  |  {n_transitions} transitions  |  "
        f"maxDepth={maxDepth}  maxBreadth={maxBreadth}",
        fontsize=11
        )
    draw_grid(axes[0], best_states[0],
            title=f"Meilleur état\n({max_zones}/{ZONE_COUNT} zones, bat={best_states[0]['battery']}%)")
    if crashed_states:
        draw_grid(axes[1], crashed_states[0], title="Exemple état crash")
    else:
        draw_grid(axes[1], make_initial_state(), title="Aucun crash trouvé")
    plt.tight_layout()
    plt.show()
    return visited, transitions





   
#Main //////////////////////////////////
if __name__=="__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python drone.py interactif")
        print("  python drone.py automatique <fichier.csv>")
        print("  python drone.py exhaustif")
        sys.exit(0)


    mode = sys.argv[1].lower()
    if mode =="interactif":
        mode_interactif()
    elif mode == "automatique":
        if len(sys.argv)<3:
            print("veuillez ajouter le fichier csv correspondant")
        else:
            mode_automatique(sys.argv[2])
    elif mode=="exhaustif":
        md = int(sys.argv[2]) if len(sys.argv) > 2 else -1
        mb = int(sys.argv[3]) if len(sys.argv) > 3 else -1
        mode_exhaustif(md, mb)

    else:
        print(f"mode inconnu")
    














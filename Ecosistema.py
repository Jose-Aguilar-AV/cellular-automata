from manim import *
import random

class EcosystemAutomaton(Scene):
    def construct(self):
        
        grid_size = 15  
        cell_size = 0.45 
        steps = 20  
        max_animations = 70  
        animation_count = 0  

        legend = VGroup(
            Text("Datos:", font_size=24),
            Text("Recurso (verde)", font_size=20, color=GREEN),
            Text("Presa (blanco)", font_size=20, color=WHITE),
            Text("Depredador (naranja)", font_size=20, color=ORANGE),
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UP + LEFT)

        grid = VGroup()
        cells = {}  
        
        for i in range(grid_size):
            for j in range(grid_size):
                cell = Square(side_length=cell_size)
                cell.move_to([i * cell_size - (grid_size * cell_size) / 2, 
                              j * cell_size - (grid_size * cell_size) / 2, 0])
                cells[(i, j)] = cell
                grid.add(cell)

        grid.set_stroke(width=0.5, color=GRAY)
        self.play(Create(grid), Write(legend))

        def random_position():
            return (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))

        def add_element(position, color):
            i, j = position
            circle = Dot(radius=0.2, color=color)
            circle.move_to(cells[(i, j)].get_center())
            circle.position = (i, j)  
            circle.steps_since_eat = 0  
            circle.recent_meals = 0  
            return circle

        resources = [add_element(random_position(), GREEN) for _ in range(15)]
        preys = [add_element(random_position(), WHITE) for _ in range(5)]
        predators = [add_element(random_position(), ORANGE) for _ in range(3)]

        elements = VGroup(*resources, *preys, *predators)
        self.play(FadeIn(elements))

        def get_neighbors(position):
            i, j = position
            neighbors = []
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < grid_size and 0 <= nj < grid_size:
                        neighbors.append((ni, nj))
            return neighbors

        def play_with_limit(animation):
            nonlocal animation_count
            if animation_count < max_animations:
                self.play(animation)
                animation_count += 1

        def move_element(element, elements_group, grid_size):
            i, j = element.position
            neighbors = get_neighbors((i, j))
            random.shuffle(neighbors)

            for new_i, new_j in neighbors:
                if not any(e.position == (new_i, new_j) for e in elements_group):
                    element.move_to(cells[(new_i, new_j)].get_center())
                    element.position = (new_i, new_j)
                    break

        def process_prey(prey, resources, preys):
            i, j = prey.position
            prey.steps_since_eat += 1

            found_resource = False
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue  
                    ni, nj = i + di, j + dj
                    if 0 <= ni < grid_size and 0 <= nj < grid_size:
                        for resource in resources:
                            if resource.position == (ni, nj):
                                resources.remove(resource)
                                play_with_limit(FadeOut(resource))
                                prey.steps_since_eat = 0
                                prey.recent_meals += 1

                                if prey.recent_meals == 1:  
                                    neighbors = get_neighbors(prey.position)
                                    random.shuffle(neighbors)
                                    for ni, nj in neighbors:
                                        if not any(e.position == (ni, nj) for e in resources + preys + predators):
                                            new_prey = add_element((ni, nj), WHITE)
                                            preys.append(new_prey)
                                            play_with_limit(FadeIn(new_prey))
                                            prey.recent_meals = 0
                                            break
                                break  
                        if found_resource:
                            break
            if not found_resource:
                move_element(prey, preys + predators, grid_size)
                            
            if prey.steps_since_eat > 6:
                preys.remove(prey)
                play_with_limit(FadeOut(prey))


        def process_predator(predator, preys, predators):
            i, j = predator.position
            predator.steps_since_eat += 1

            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue 
                    ni, nj = i + di, j + dj
                    if 0 <= ni < grid_size and 0 <= nj < grid_size:
                        for prey in preys:
                            if prey.position == (ni, nj):
                                preys.remove(prey)
                                play_with_limit(prey.animate.set_color(ORANGE))
                                play_with_limit(FadeOut(prey))
                                predator.steps_since_eat = 0
                                predator.recent_meals += 1

                                neighbors = get_neighbors(predator.position)
                                random.shuffle(neighbors)
                                for ni, nj in neighbors:
                                    if not any(e.position == (ni, nj) for e in resources + preys + predators):
                                        new_predator = add_element((ni, nj), ORANGE)
                                        predators.append(new_predator)
                                        play_with_limit(FadeIn(new_predator))
                                        break
                                break  
                            
            if predator.steps_since_eat > 5:
                predators.remove(predator)
                play_with_limit(FadeOut(predator))


        def process_resources(resources):
            new_resources = []
            for resource in resources:
                neighbors = get_neighbors(resource.position)
                random.shuffle(neighbors)
                for ni, nj in neighbors:
                    if not any(e.position == (ni, nj) for e in resources + preys + predators):
                        if random.random() < 0.36:  
                            new_resource = add_element((ni, nj), GREEN)
                            new_resources.append(new_resource)
                        break
            resources.extend(new_resources)
            play_with_limit(FadeIn(VGroup(*new_resources)))

        for _ in range(steps):
            for prey in list(preys):
                move_element(prey, preys + predators, grid_size)
                process_prey(prey, resources, preys)
            for predator in list(predators):
                move_element(predator, preys + predators, grid_size)
                process_predator(predator, preys, predators)
            process_resources(resources)
            self.wait(0.0001)

        self.wait(0.1)

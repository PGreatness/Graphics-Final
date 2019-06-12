import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = ''
    num_frames = 1
    for command in commands:
        if command['op'] == 'basename':
            name = command['args'][0]
        if command['op'] == 'frames':
            num_frames = command['args'][0]
    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropriate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(int(num_frames)) ]
    for command in commands:
        if command['op'] == 'vary':
            knob = command['knob']
            args = command['args']
            print(command)
            print(args)
            length = args[1] - args[0]
            speed = args[3] - args[2]
            change = speed / length
            for i in range(int(length)):
                frames[int(i + args[0])][knob] = args[2] + change * i
    print("This is frames:\n")
    print(frames)
    return frames

# all the knobs in the current MDL file
def third_pass( commands ):
    knob_list = []
    for command in commands:
        if command['op'] == 'vary':
            if command['knob'] not in knob_list:
                knob_list.append(command['knob'])
    return knob_list

def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)
    kb_list = third_pass( commands )

    tmp = new_matrix()
    ident( tmp )

    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 100
    consts = ''
    coords = []
    coords1 = []
    i = 0
    new_sets = {}
    set_all = False
    for frame in frames:
        symbols.update(frame)
        tmp = new_matrix()
        ident(tmp)
        stack = [ [ x for x in tmp ] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []

        for command in commands:
            print(command)
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'set':
                symbols['knob'] = args[0]
                new_sets[command['knob']] = args[0]
                print(symbols)

            if c == 'set_knobs':
                k = symbols.keys()
                for w in k:
                    if w in kb_list:
                        symbols[w] = args[0]
                        new_sets[w] = args[0]
                print(symbols)
                set_all = True

            if c == 'save_knobs':
                print(command)
                knob = command['knob_list']
                knob_list = {knob:[ x[knob] for x in frames if knob in x]}
                print(knob_list)
                symbols["knob_list"] = knob_list

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                        args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                print('Got 1')
                add_torus(tmp,
                        args[0], args[1], args[2], args[3], args[4], step_3d)
                print('got 2')
                matrix_mult( stack[-1], tmp )
                print('got 3')
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                print('got 4')
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                        args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                vel = 1
                if command['knob'] is not None:
                    vel = new_sets[command['knob']] if not NameError else symbols[command['knob']]
                print(vel)
                print(new_sets)
                tmp = make_translate(args[0] * vel, args[1] * vel, args[2] * vel)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                vel = 1
                if command['knob'] is not None:
                    vel = new_sets[command['knob']] if not NameError else symbols[command['knob']]
                tmp = make_scale(args[0] * vel, args[1] * vel, args[2] * vel)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                vel = 1
                if command['knob'] is not None:
                    vel = new_sets[command['knob']] if not NameError else symbols[command['knob']]
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta * vel)
                elif args[0] == 'y':
                    tmp = make_rotY(theta * vel)
                else:
                    tmp = make_rotZ(theta * vel)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
            # end operation loop
        print('/anim/' + name + "%03d"%i)
        save_extension(screen, 'anim/' + name + "%03d"%i + '.gif')
        i += 1
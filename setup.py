import cx_Freeze

executables = [cx_Freeze.Executable('Tetris.py')]

cx_Freeze.setup(
    name='Tetris',
    options={'build_exe':{'packages':['pygame'],
                          'include_files':['highScore.txt',
                          'faileffect.wav', 'maintheme.mid',
                          'tetris_title.png', 'gameover.mid']}},
    executables = executables


    )


        

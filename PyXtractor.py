import os, commands

class pyx:
    def __init__( self ):
        self.default_config = commands.getstatusoutput('sex -d')[1].split('\n')  ### get a default config file
        param_list0     = commands.getstatusoutput('sex -dp')[1].split('\n') ### get a full list of params

        self.default_conv   = 'CONV NORM\n1 2 1\n2 4 2\n1 2 1\n' ### a hard-coded filter to fall back on

        self.options = {}

        for k in self.default_config:
            if k[0] == '#':
                continue
            k1 = k.split('#') ### break on comment char
            k  = k1[0].strip().split()

            if len(k) == 0:
                continue
            elif len(k) == 1: ### default = ''
                self.options[ k[0] ] = ''
            elif len(k) == 2:
                self.options[ k[0] ] = k[1]
            else:
                p = ' '.join( k[1:] )
                self.options[ k[0] ] = p
                
        self._param_list = []
        for k in param_list0:
            k = k[1:].split()[0]
            self._param_list.append( k )

        self.params = [ 'X_IMAGE', 'Y_IMAGE', 'MAG_AUTO' ]

                
    def getcat( self, image ):

        ### lets do some checks:
        for k in self.params:
            if self._param_list.count( str( k ) ) == 0:
                print 'Param %s not a Source Extractor parameter - quitting.'
                sys.exit(-1)

        FILE = open( self.options[ 'PARAMETERS_NAME' ], 'w')
        for k in self.params:
            FILE.write('%s\n'%( k.strip() ) )
        FILE.close()

        FILE = open( 'PyX.config', 'w')
        for k in self.options:
            FILE.write('%s %s\n'%( k, str(self.options[k]).strip() ) )
        FILE.close()
                
        if not os.path.isfile( self.options[ 'FILTER_NAME' ] ):
            if self.options[ 'FILTER' ] == 'Y':
                print 'Requested filter not found - using default.conv' 
            FILE = open('default.conv', 'w')
            FILE.write( self.default_conv )
            FILE.close()
                
        sysout = commands.getstatusoutput('sex -c PyX.config %s'%(image) )

    def readcat( self ):
        print 'not implemented yet - will read from self.options[ CATALOG_NAME ] and return...'

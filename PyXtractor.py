import os, commands, sys, asciidata, numpy

class pyx:
    def __init__( self ):
        self.default_config = commands.getstatusoutput('sex -dd')[1].split('\n')  ### get a default config file
        param_list0         = commands.getstatusoutput('sex -dp')[1].split('\n') ### get a full list of params

        self.default_conv   = 'CONV NORM\n1 2 1\n2 4 2\n1 2 1\n' ### a hard-coded filter to fall back on

        self.options = {}

	self.options_description = {}

        for k in self.default_config:
	    try:
		if k[0] == '#':
		    continue

		k1 = k.split('#') ### break on comment char
		k  = k1[0].strip().split()

		if len(k) == 0:
		    continue

		if len(k) == 1: ### default = ''
		    self.options[ k[0] ] = ''
		elif len(k) == 2:
		    self.options[ k[0] ] = k[1]
		else:
		    p = ' '.join( k[1:] )
		    self.options[ k[0] ] = p

		k2 = k1[1].strip()
		self.options_description[ k[0] ] = 'Option %s: %s'%(k[0], k2)
	    except:
		### Probably a zero-length line or something.
		continue

        self._param_list = []
        for k in param_list0:
            k = k[1:].split()[0]
            self._param_list.append( k )

        self.params = [ 'X_IMAGE', 'Y_IMAGE', 'MAG_AUTO' ]

	self.options['CATALOG_NAME'] = 'PyX.cat'
	self.options['CATALOG_TYPE'] = 'ASCII_HEAD'
	self.catalog = {}
                
    def getcat( self, image ):

        ### lets do some checks:
        for k in self.params:
            if self._param_list.count( str( k ) ) == 0:
                print 'Param %s not a Source Extractor parameter - quitting.'%( str( k ) )
                sys.exit(1)

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

	    if not os.path.isfile('default.conv'):
		FILE = open('default.conv', 'w')
		FILE.write( self.default_conv )
		FILE.close()
                
        sysout = commands.getstatusoutput('sex -c PyX.config %s'%(image) )
	self.catalog = self.readcat()

    def readcat( self ):

	data_dict = {}
	if self.options['CATALOG_TYPE'] == 'ASCII_HEAD':
	    CAT = asciidata.open(self.options['CATALOG_NAME'])

	    for k in self.params:
		data_dict[k] = numpy.asarray( CAT[k] )

	    return data_dict

	else:
	    print 'Cannot read CATALOG_TYPE %s'%( self.options['CATALOG_TYPE'] )
	    print 'Cannot set CATALOG_TYPE to ASCII_HEAD'

	    return {}


def example( ):
    print 'Example simple PyX extraction.'
    fn = raw_input('Please enter .fits image file name: ')
    
    T = pyx()  ### Initialize a pyx object 'T'

    ### Default params are X_IMAGE Y_IMAGE MAG_AUTO
    ### and are kept in T.params
    ### Lets add another...
    T.params.append( 'FLAGS' )

    ## lets print all the params:
    print 'Params to generate: %s'%( ' '.join( T.params ) )
    

    ### All the configuration params are kept in dictionary:
    ### T.options
    ### Lets change a couple of them
    T.options['DETECT_THRESH']  = 5.0
    T.options['DETECT_MINAREA'] = 3

    ### Let's see what the second one of these means:
    print T.options_description['DETECT_MINAREA']

    ### Happy? Alright! Lets run it. Pass .getcat( ) a .fits filename.
    T.getcat( fn )

    ### self.catalog is a python dictionary containing keywords of params
    ### and numpy arrays of extracted data.
    print T.catalog['FLAGS']

    return T.catalog


if __name__ == "__main__":
    catalog = example()

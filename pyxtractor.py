import os, commands, sys, numpy, tempfile

__version__ = '0.3'

### Quick check to ensure that Source Extractor is installed.
S_version = commands.getstatusoutput('sex -v')
if S_version[0] != 0:
    print 'Source Extractor not found.'
    print 'Returns: %s'%( S_version[1] )
    sys.exit(-1)

try:
    import asciidata
except ImportError:
    print 'Did not find asciidata; falling back on slow parsing.'
    pass

class pyx:

    ''' The pyx class: generates an object that allows you to interact with Source Extractor
    in a straightforward way.
    
    On invocation, pyx reads in the default configuration and parameter files for Source Extractor.

    Those files are then parsed as python dictionaries, giving you access to all of their keys.

    Once you have modified any of the config or param dictionaries to your liking, you can
    tell pyx to run Source Extractor by calling pyx.getcat( [ 'list', 'of', 'image', 'names' ] )

    Temporary configuration and parameter files will be written, Source Extractor will run,
    and the resulting catalogs will be read in to further python dictionaries inside pyx.catalog

    eg, for image foo.fits and bar.fits

    from pyxtractor import pyx
    T = pyx()
    T.params = [ 'X_IMAGE', 'Y_IMAGE', 'MAG_APER' ]   <-- this will tell pyx to read these three params.
    T.options[ 'DETECT_THRESH' ] = 10                 <-- only detect sources over 10 sigma.
    T.getcat( ['foo.fits', 'bar.fits'] )              <-- Source Extractor runs!
    T.catalog[ 'Ifoo.fits' ]
         {'X_IMAGE': array([ 1518.199,  1289.258,  1127.766, ...,  1234.537,   292.327,  1961.47 ]), 
 	  'Y_IMAGE': array([  900.927,  1005.062,  1010.344, ...,  3441.268,  3417.599, 3443.261]), 
	  'MAG_APER': array([-18.7066, -17.1244, -14.3642, ..., -13.3924, -13.93  , -11.2913])}
    Note that in pyx.catalog, all image name keys have I pre-pended on them. This is to avoid any
    issues with non-alpha characters leading in python dictionary keys.

    '''

    def __init__( self ):
        self.default_config = commands.getoutput('sex -dd').split('\n')  ### get a default config file
        param_list0         = commands.getoutput('sex -dp').split('\n') ### get a full list of params

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
            try:
                k = k[1:].split()[0]
                self._param_list.append( k )
            except:
                continue
                
        self.params = [ 'X_IMAGE', 'Y_IMAGE', 'MAG_AUTO' ]

        catalog_file = tempfile.mkstemp(suffix='.cat', prefix='tmpPyX.', dir='./')[1]
        self.options['CATALOG_NAME'] = catalog_file

        param_file = tempfile.mkstemp(suffix='.param', prefix='tmpPyX.', dir='./')[1]
        self.options[ 'PARAMETERS_NAME' ] = param_file

        self.tmpfiles = [catalog_file, param_file]

        self.options['CATALOG_TYPE'] = 'ASCII_HEAD'
        self.catalog = {}

    def getcat( self, imageV ):

        ### lets do some checks:
        for k in self.params:
            if str(k) not in self._param_list:
                print 'Param %s not a Source Extractor parameter - quitting.'%( str( k ) )
                sys.exit(1)

        #print self.options[ 'PARAMETERS_NAME' ]
                
        FILE = open( self.options[ 'PARAMETERS_NAME' ], 'w')
        for k in self.params:
            FILE.write('%s\n'%( k.strip() ) )
        FILE.close()

        config_file = tempfile.mkstemp(suffix='.config', prefix='tmpPyX.', dir='./')[1]

        self.tmpfiles.append( config_file )

        if not os.path.isfile( self.options[ 'FILTER_NAME' ] ):
            #if self.options[ 'FILTER' ] == 'Y':
            #print 'Requested filter not found - using defaultPyX.conv' 
            self.options[ 'FILTER_NAME' ] = 'defaultPyX.conv'

        if not os.path.isfile('defaultPyX.conv'):
            FILE = open('defaultPyX.conv', 'w')
            FILE.write( self.default_conv )
            FILE.close()
            
        FILE = open( config_file, 'w')
        for k in self.options:
            FILE.write('%s %s\n'%( k, str(self.options[k]).strip() ) )
        FILE.close()

            
        if type(imageV) == type(str()):
            ### you passed a single imagename, therefore:
            sysout = commands.getstatusoutput('sex -c %s %s'%(config_file, imageV) )

            if sysout[0] != 0:
                print 'Warning: Command sex -c PyX.config %s raised the following error:'%(image)
                print sysout

            self.catalog[ '%s'%(imageV) ] = self.readcat()


        else:
            ### imageV had better be an iterable object.
            for image in imageV:

                sysout = commands.getstatusoutput('sex -c %s %s'%(config_file, image) )

                if sysout[0] != 0:
                    print 'Warning: Command sex -c PyX.config %s raised the following error:'%(image)
                    print sysout

                self.catalog[ '%s'%(image) ] = self.readcat()


    def readcat( self ):

        data_dict = {}

        ### Lets see which packages we need to fall back on.
        try:
            __import__('asciidata')
        except ImportError:
            do_read = True
        else:
            do_read = False

        if self.options['CATALOG_TYPE'] == 'ASCII_HEAD':

            if not do_read:
                CAT = asciidata.open(self.options['CATALOG_NAME'])

                for k in self.params:
                    data_dict[k] = numpy.asarray( CAT[k] )

            else:
                FILE = open(self.options['CATALOG_NAME'])
                dat  = FILE.readlines()
                FILE.close()

                for k in self.params:
                    data_dict[k] = []

                for k in dat:
                    if k[0] == '#':
                        continue
                    k1 = k.strip().split()
                    for j in range(0,len(self.params)):
                        data_dict[ self.params[j] ].append( k1[j] )

                for k in self.params: ### turn the python arrays into numpy float arrays.
                    data_dict[k] = numpy.asarray( data_dict[k], dtype='float')

            return data_dict

        else:
            print 'Cannot read CATALOG_TYPE %s'%( self.options['CATALOG_TYPE'] )
            print 'Cannot set CATALOG_TYPE to ASCII_HEAD'

            return {}


    def cleanup( self ):
        for path in self.tmpfiles:
            if os.path.isfile( path ):
                os.system('rm %s'%( path ) )
        self.tempfiles = []
	

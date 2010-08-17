# Forecast support, experimental coding
# probably all this will be rewritten, put in a different directory, etc.

import numpy
import cdtime
import cdms2
import copy
from cdms2 import CDMSError

def two_times_from_one( t ):
    """Input is a time representation, either as the long int used in the cdscan
    script, or as a cdtime comptime (component time) object.  Output is the same
    time, using _both_ types."""
    if t==0:
        t = 0L
    if isinstance(t,long):
        tl = t
        year = tl / 1000000000L
        rem = tl % 1000000000L
        month = rem / 10000000L
        rem =   rem % 10000000L
        day =     rem / 100000
        allsecs = rem % 100000
        sec =     allsecs%60
        allmins = allsecs/60
        min =  allmins%60
        hour = allmins/60
        tc = cdtime.comptime(year,month,day,hour,min,sec)
    else:
        # I'd like to check that t is type comptime, but although Python
        # prints the type as <type 'comptime'> it won't recognize as a type
        # comptime or anything similar.  Note that cdtime.comptime is a C
        # function available from Python.
        tc = t
        tl = tc.year * 1000000000L
        tl += tc.month * 10000000L
        tl += tc.day   * 100000
        tl += tc.hour * 3600
        tl += tc.minute *60
        tl += tc.second.__int__()
    return tl,tc

class forecast():
    """represents a forecast starting at a single time"""

    def __init__( self, tau0time, dataset_list, path="" ):
        """tau0time is the first time of the forecast, i.e. the time at which tau=0.
        dataset_list is used to get the forecast file from the forecast time.
        Each list item should look like this example:
        [None, None, None, None, 2006022200000L, 'file2006-02-22-00000.nc']
        Normally dataset_list = fm[i][1] where fm is the output of
        cdms2.dataset.parseFileMap and fm[i][0] matches the variables of interest.

        N.B.  This is like a CdmsFile.  Creating a forecast means opening a file,
        so later on you should call forecast.close() to close it.
        """
        self.fctl, self.fct = two_times_from_one( tau0time )

        filenames = [ l[5] for l in dataset_list if l[4]==self.fctl ]
        if len(filenames)>0:
            filename = filenames[0]
        else:
            raise CDMSError, "Cannot find filename for forecast %d"%self.fctl
        self.filename = path + '/' + filename
        self.file = cdms2.open( self.filename )

    def close( self ):
        self.file.close()

    def __call__( self, varname ):
        """Reads the specified variable from this forecast's file."""
        return self.file(varname)

    def __getitem__( self, varname ):
        """Reads variable attributes from this forecast's file."""
        return self.file.__getitem__(varname)

    def __repr__(self):
        return "<forecast from %s>"%(self.fct)
    __str__ = __repr__


class forecasts():
    """represents a set of forecasts"""

# >>> There should be a way to determine what forecast_times are available
# >>> Also, we _could_ have a default forecast_times to be "all times",
# >>> but I'm inclined to require the times so as to open no more files than
# >>> needed.  Is that really an issue?

    def __init__( self, dataset_file, forecast_times, path="" ):
        """Creates a set of forecasts.  Normally you do it by something like
        f = forecasts( 'file.xml', (min_time, max_time) )
        or
        f = forecasts( 'file.xml', (min_time, max_time), '/home/me/data/' )
        or
        f = forecasts( 'file.xml', [ time1, time2, time3, time4, time5 ] )
        where the two or three arguments are::
        1. the name of a dataset xml file generated by "cdscan --forecast ..."
        2. Times here are the times when the forecasts began (tau=0).
        If you use a tuple, forecasts will be chosen which start at a time t with
        min_time <= t < max_time .  If you use a list, it will be the exact
        start (tau=0) times for the forecasts to be included.
        Times can be specified either as 13-digit long integers, e.g.
        2006012300000 for the first second of January 23, 2006, or as
        component times (comptime) in the cdtime module.
        3. An optional path for the data files; use this if the xml file
        contains filenames without complete paths.
         
        As for the forecast class, this opens files when initiated, so when you
        are finished with the forecats, you should close the files by calling
        forecasts.close() .
        """
   # >>>> maybe it's ok, or better, to close files in here, think & try <<<<<

        # Create dataset_list to get a forecast file from each forecast time.
        self.dataset=cdms2.openDataset( dataset_file, dpath=path )
        fm=cdms2.dataset.parseFileMap(self.dataset.cdms_filemap)
        self.alltimesl =[ f[4] for f in fm[0][1] ]  # 64-bit (long) integers
        dataset_list = fm[0][1]
        for f in fm[1:]:
            dataset_list.extend(f[1])

        if type(forecast_times) is tuple:
            tlo = forecast_times[0]
            if type(tlo) is not long:  # make tlo a long integer
                tlo, tdummy = two_times_from_one( tlo )
            thi = forecast_times[1]
            if type(thi) is not long:  # make thi a long integer
                thi, tdummy = two_times_from_one( thi )
            mytimesl = [ t for t in self.alltimesl if (t>=tlo and t<thi) ]
            self.fcs = [ forecast( t, dataset_list, path ) for t in mytimesl ]
        elif type(forecast_times) is list:
            self.fcs = [ forecast( t, dataset_list, path ) for t in forecast_times ]
        else:
            self.fcs = []
            raise CDMSError, "bad argument to forecasts.__init__"

    def reduce_inplace( self, min_time, max_time ):
        """ For a forecasts object f, f( min_time, max_time ) will reduce the
        scope of f, to forecasts whose start time t has min_time<=t<max_time.
        This is done in place, i.e. any other forecasts in f will be discarded.
        If slice notation were possible for forecasts (it's not because we need
        too many bits to represent time), this function would do the same as
        f = f[min_time : max_time ]
        If you don't want to change the original "forecasts" object, just do
        copy.copy(forecasts) first.
        Times can be the usual long integers or cdtime component times.
        """
        tlo, tdummy = two_times_from_one( min_time )
        thi, tdummy = two_times_from_one( max_time )
        self.fcs = [ f for f in self.fcs if ( f.fctl>=tlo and f.fctl<thi ) ]

    def close( self ):
        self.dataset.close()
        for fc in self.fcs:
            fc.close()

    def __call__( self, varname ):
        """Reads the specified variable for all the forecasts.
        Creates and returns a new variable which is dimensioned by forecast
        as well as the original variable's dimensions.
        """
        # Assumptions include: For two forecasts, f1('var') and f2('var') are
        # the same variable in all but values - same names, same domain,
        # same units, same mask, etc.
        # Note: Why can't we start out by doing self.dataset(varname) as in
        # __getitem__?  That's simpler to code, but in this case it would require
        # reading large amounts of data from files, only to throw it away.

        # Create the variable from the data, with mask:
        vars = [ fc(varname) for fc in self.fcs ]
        v0 = vars[0]
        a = numpy.asarray([ v.data for v in vars ])
        if v0._mask == False:
            m = False
            v = cdms2.tvariable.TransientVariable( a )
        else:
            m = numpy.asarray([ v._mask for v in vars])
            v = cdms2.tvariable.TransientVariable( a, mask=m, fill_value=v0._fill_value )

        # Domain-related attributes:
        ltvd = len(v0._TransientVariable__domain)
        v._TransientVariable__domain[1:ltvd+1] = v0._TransientVariable__domain[0:ltvd]
        v._TransientVariable__domain[0] = self.forecast_axis( varname )
        if hasattr( v0, 'coordinates' ):
            v.coordinates = 'iforecast ' + v0.coordinates

        # Other attributes, all those for which I've seen nontrivial values in a
        # real example (btw, the _isfield one was wrong!) :
        if hasattr( v0, 'id' ):
            v.id = v0.id
        if hasattr( v0, 'long_name' ):
            v.long_name = v0.long_name
        if hasattr( v0, 'base_name' ):
            v.base_name = v0.base_name
        if hasattr( v0, 'units' ):
            v.units = v0.units
        if hasattr( v0, '_isfield' ):
            v._isfield = v0._isfield
        return v

    def forecast_axis( self, varname ):
        """returns a tuple (axis,start,length,true_length) where axis is in the
        forecast direction"""
        # TO DO: see whether I can get an axis without starting with a variable name.
        # Most variables will have a suitable domain.

        var = self.dataset[varname]
        # ... var is a DatasetVariable, used here just for its domain
        dom = copy.deepcopy(getattr(var,'domain',[]))
        # ...this 'domain' attribute has an element with an axis, etc.
        # representing all forecasts; so we want to cut it down to match
        # those forecasts in self.fcs.
        for domitem in dom:
            # The domain will have several directions, e.g. forecast, level, latitude.
            # There should be only one forecast case, named fctau0.
            # domitem is a tuple (axis,start,length,true_length) where
            # axis is a axis.Axis and the rest of the tuple is int's.
            # I don't know what true_length is, but it doesn't seem to get used
            # anywhere, and is normally the same as length.
            if getattr(domitem[0],'id',None)=='fctau0':
                # Force the axis to match self.fcs :
                # More precisely the long int times self.fcs[i].fctl should match
                # the axis data. The axis partition and .length need changing too.
                domitem1 = 0
                domitem2 = len(self.fcs)
                domitem3 = len(self.fcs)
                axis = copy.copy(domitem[0])
                axis._data_ = [ f.fctl for f in self.fcs ]
                axis.length = len(axis._data_)
                axis.partition = axis.partition[0:axis.length]
        return ( axis, domitem1, domitem2, domitem3 )


    def __getitem__( self, varname ):
        """returns whatever the forecast set has that matches the given
        attribute, normally a DatasetVariable.
        """
        if type(varname) is not str :
            raise CDMSError, "bad argument to forecasts[]"

        var = self.dataset[varname]
        # var is a DatasetVariable and consists of lots of attributes.

        # The attribute which needs to be changed is 'domain' - it will normally
        # have an element with an axis, etc. representing all forecasts; so we
        # want to cut it down to match those forecasts in self.fcs.
        dom = copy.deepcopy(getattr(var,'domain',[]))
        for i in range(len(dom)):
            domitem = dom[i]
            if getattr(domitem[0],'id',None)=='fctau0':
                dom[i] = self.forecast_axis(varname)
        setattr(var,'domain',dom)
                
        return var

    def __repr__(self):
        l = len(self.fcs)
        if l==0:
            return "<forecasts - None>"
        else:
            return "<forecasts from %s,...,%s>"%(self.fcs[0].fct,self.fcs[l-1].fct)
    __str__ = __repr__


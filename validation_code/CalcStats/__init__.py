from __future__ import division, print_function
import numpy as np

def L2Diff(dataset_1, dataset_2, threshold=1.0, details=False):
    """
    compute the L2 norm for 2 datasets
    
    checks the x values to see if interpolation is needed
    threshold sets criterion for passing the test
    
    Parameters
    ----------
    dataset_1 : dictionary
        data to be validated against
        
        x : independent variable
        
        y : dependent variable
        
        y+ : asymmetric positive error on y
        
        y- : asymmetric negative error on y
        
        dy : 1-sigma symmetric error on y
        
    dataset_2 : dictionary
        validation data 
    
    threshold : float, optional
    
    Returns
    -------
    L2 : float
    
    sucess : boolean
    
    Notes
    -----
    Errors are assumed to be un-correlated.
    
    If assymetric errors on `y` are provided, the mean of the postive and 
    negative errors are taken. This is clearly not the 'correct' thing to do.
    """
    
    #clean up catalog 1 data to remove nans and infs
    mask=np.isfinite(np.vstack(dataset_1.values())).all(axis=0)
    x1 = dataset_1['x'][mask]
    y1 = dataset_1['y'][mask]
    #extract errors if they exist
    if(dataset_1.has_key('y+') and dataset_1.has_key('y-')):
        e1 = (dataset_1['y+'][mask]-dataset_1['y-'][mask])/2.
    elif(dataset_1.has_key('dy')):
        e1 = dataset_1['dy'][mask]
    else:
        e1 = None

    #check for zero errors and remove
    if e1 is not None:
        emask = (e1 > 0.)
        if (np.sum(emask) < len(emask)):
            print ("Removed "+str(len(emask)-np.sum(emask))+" zero-error points from dataset #1 for L2 test")
            e1=e1[emask]
            x1=x1[emask]
            y1=y1[emask]
                
    #clean up catalog 2 data to remove nans and infs
    mask=np.isfinite(np.vstack(dataset_2.values())).all(axis=0)
    x2 = dataset_2['x'][mask]
    y2 = dataset_2['y'][mask]
    #extract errors if they exist
    if(dataset_2.has_key('y+') and dataset_2.has_key('y-')):
        e2 = (dataset_2['y+'][mask]-dataset_2['y-'][mask])/2.
    elif(dataset_2.has_key('dy')):
        e2 = dataset_2['dy'][mask]
    else:
        e2 = None

    #check for zero errors and remove
    if e2 is not None:
        emask = (e2 > 0.)
        if (np.sum(emask) < len(emask)):
            print ("Removed "+str(len(emask)-np.sum(emask))+" zero-error points from dataset #2 for L2 test")
            e2=e2[emask]
            x2=x2[emask]
            y2=y2[emask]
    
    #ensure ranges of catalog and validation data are the same
    minx=max(np.min(x1),np.min(x2))
    maxx=min(np.max(x1),np.max(x2))
    select1=(x1>=minx) & (x1<=maxx)
    select2=(x2>=minx) & (x2<=maxx)
    x1=x1[select1]
    x2=x2[select2]
    y1=y1[select1]
    y2=y2[select2]
    if e1 is not None:
        e1=e1[select1]
    if e2 is not None:
        e2=e2[select2]
    
    #interpolate catalog data to data x-points
    if not(np.all(x1==x2)):
        y1int = np.interp(x2, x1, y1)
        if e1 is not None:
            e1int = np.interp(x2, x1, e1)
    else:
        y1int=y1
        if e1 is not None:
            e1int = e1
    
    #compute L2 norm
    if e1 is not None:
        if e2 is not None:
            diff = (y2 - y1int)**2 / (e1int**2 + e2**2)            
        else:
            diff = (y2 - y1int)**2 / e1int**2
    else:
        if e2 is not None:
            diff = (y2 - y1int)**2 / e2**2 
        else:
            diff = (y2 - y1int)**2
    diff=np.sqrt(diff)
    L2= np.sum(diff)
    
    #normalize by the number of points
    N_points = 1.0*len(y2)
    L2 = L2/N_points

    #return result
    if (L2 > threshold) or (np.isnan(L2)):
        success = False
    else:
        success = True
    
    if (details):
        #save detailed results to dictionary if requested
        if e1 is not None:
            if e2 is not None:
                results={'diff':diff,'x':x2,'y1int':y1int,'y2':y2,'e1int':e1int,'e2':e2}
            else:
                results={'diff':diff,'x':x2,'y1int':y1int,'y2':y2,'e1int':e1int}
        else:
            if e2 is not None:
                results={'diff':diff,'x':x2,'y1int':y1int,'y2':y2,'e2':e2}
            else:
                results={'diff':diff,'x':x2,'y1int':y1int,'y2':y2}

        return L2, success, results
    else:
        return L2, success
    

def L1Diff(dataset_1, dataset_2, threshold=1.0, details=False):
    """
    compute the L1 norm for 2 datasets
    
    checks the x values to see if interpolation is needed
    threshold sets criterion for passing the test
    
    Parameters
    ----------
    dataset_1 : dictionary
        data to be validated against
        
        x : independent variable
        
        y : dependent variable
                
    dataset_2 : dictionary
        validation data 
    
    threshold : float, optional
    
    Returns
    -------
    L1 : float
    
    sucess : boolean
    
    Notes
    -----
    Errors are assumed to be un-correlated.
    
    If assymetric errors on `y` are provided, the mean of the postive and 
    negative errors are taken. This is clearly not the 'correct' thing to do.
    """
    
    #clean up catalog 1 data to remove nans and infs
    mask=np.isfinite(np.vstack(dataset_1.values())).all(axis=0)
    x1 = dataset_1['x'][mask]
    y1 = dataset_1['y'][mask]
    
    #clean up catalog 2 data to remove nans and infs
    mask=np.isfinite(np.vstack(dataset_2.values())).all(axis=0)
    x2 = dataset_2['x'][mask]
    y2 = dataset_2['y'][mask]
    
    #ensure ranges of catalog and validation data are the same
    minx=max(np.min(x1),np.min(x2))
    maxx=min(np.max(x1),np.max(x2))
    select1=(x1>=minx) & (x1<=maxx)
    select2=(x2>=minx) & (x2<=maxx)
    x1=x1[select1]
    x2=x2[select2]
    y1=y1[select1]
    y2=y2[select2]
    
    #interpolate catalog data to data x-points
    if not(np.all(x1==x2)):
        y1int = np.interp(x2, x1, y1)
    else:
        y1int=y1
    
    #compute L1 norm and significance
    diff= np.abs(y2 - y1int)
    L1 = np.sum(diff)
    
    #normalize by the number of points
    N_points = 1.0*len(y2)
    L1 = L1/N_points
    
    #return result
    if (L1 > threshold) or (np.isnan(L1)):
        success = False
    else:
        success = True

    if (details):
        #save detailed results to dictionary if requested
        results={'diff':diff,'x':x2,'y1int':y1int,'y2':y2}
        return L1, success, results
    else:
        return L1, success
    

def KS_test(dataset_1, dataset_2, threshold=1.0, details=False):
    """
    compute the K-S statistic for 2 datasets (CDFs)
    
    checks the x values to see if interpolation is needed
    threshold sets criterion for passing the test
    
    Parameters
    ----------
    dataset_1 : dictionary
        data to be validated against
        
        x : independent variable
        
        y : dependent variable
                
    dataset_2 : dictionary
        validation data 
    
    threshold : float, optional
    
    Returns
    -------
    KS : float
    
    sucess : boolean
    
    """
    
    #clean up catalog 1 data to remove nans and infs
    mask=np.isfinite(np.vstack(dataset_1.values())).all(axis=0)
    x1 = dataset_1['x'][mask]
    y1 = dataset_1['y'][mask]
    
    #clean up catalog 2 data to remove nans and infs
    mask=np.isfinite(np.vstack(dataset_2.values())).all(axis=0)
    x2 = dataset_2['x'][mask]
    y2 = dataset_2['y'][mask]
    
    #ensure ranges of catalog and validation data are the same
    minx=max(np.min(x1),np.min(x2))
    maxx=min(np.max(x1),np.max(x2))
    select1=(x1>=minx) & (x1<=maxx)
    select2=(x2>=minx) & (x2<=maxx)
    x1=x1[select1]
    x2=x2[select2]
    y1=y1[select1]
    y2=y2[select2]

    #interpolate catalog data to data x-points
    if not(np.all(x1==x2)):
        y1int = np.interp(x2, x1, y1)
    else:
        y1int=y1
    
    #compute the K-S statistic
    diff= np.abs(y2-y1int)
    KS = np.max(diff)
    
    #return result
    if (KS > threshold) or (np.isnan(KS)):
        success = False
    else:
        success = True
    
    if (details):
        #save detailed results to dictionary if requested
        results={'diff':diff,'x':x2,'y1int':y1int,'y2':y2}
        return KS, success, results
    else:
        return KS, success
    
    
def write_summary_details(results, filename, method='diff',comment=None):
    """
    write summary_details data file

    Parameters
    ----------
    results : dictionary

    filename : string

    comment : string
    """

    #save results to file

    if len(results)>0:
        f = open(filename, 'w')
        if comment:
            f.write('# {0}\n'.format(comment))
        #write header and results depending on dict contents
        f.write('# {0}\n'.format('Columns are: '+method+', x, y1, y2, (e1), (e2)'))
        if ('e1int' in results and 'e2' in results):
            for b, h, hn, hx, en, ex in zip(*(results[k] for k in ['diff','x','y1int','y2','e1int','e2'])):
                f.write("%13.6e %13.6e %13.6e %13.6e %13.6e %13.6e\n" % (b, h, hn, hx, en, ex))
        elif ('e1int' in results):
            for b, h, hn, hx, en in zip(*(results[k] for k in ['diff','x','y1int','y2','e1int'])):
                f.write("%13.6e %13.6e %13.6e %13.6e %13.6e\n" % (b, h, hn, hx, en))
        elif ('e2' in results):
            for b, h, hn, hx, en in zip(*(results[k] for k in ['diff','x','y1int','y2','e2'])):
                f.write("%13.6e %13.6e %13.6e %13.6e %13.6e\n" % (b, h, hn, hx, en))
        else:
            for b, h, hn, hx in zip(*(results[k] for k in ['diff','x','y1int','y2'])):
                f.write("%13.6e %13.6e %13.6e %13.6e\n" % (b, h, hn, hx))
        #f.write('Check average '+method+': %13.6e\n' %(np.sum(results['diff'])/len(results['y2'])) )
        f.close()
    else:
        msg = ('Empty summary_details dict')
        warn(msg)
    




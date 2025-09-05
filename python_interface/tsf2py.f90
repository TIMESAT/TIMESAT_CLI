subroutine tsf2py(nyr,vi,qa,td,lc,p_nclasses,landuse,p_outindex, &
  p_ignoreday,p_ylu,p_printflag,p_fitmethod,p_smooth,p_nodata,p_outlier,p_nenvi,p_wfactnum, &
  p_startmethod,p_startcutoff,p_lpbase,p_fillbase,p_hrvppformat,p_seasonmethod,p_seapar, &
  phenologicalpar, phenologicalparqa, numseasonineachyear, yfit, yfitqa, seasonfit, tseq, &
  row, col, nimg, p_outindex_num)

implicit none

integer, intent(in) :: row,col,nimg,nyr
real*4,  intent(in), dimension(row,col,nimg) :: vi,qa
integer, intent(in), dimension(nimg) :: td
integer, intent(in), dimension(row,col) :: lc
! double precision, intent(in), dimension(row,col) :: begval,begde,endval,endde


! settings
! integer, intent(in)          :: p_continuityflag                ! 0: no continuity; 1: new run; 2: re-run
integer, intent(in)          :: p_ignoreday                     ! ignore date in leap year
double precision, intent(in) :: p_ylu(2)                        ! range for y-values
integer, intent(in)          :: p_printflag                     ! plot functions and weights (1/0)
double precision, intent(in) :: p_nodata                        ! no data from outputs ! NEW
integer, intent(in)          :: p_outlier                       ! outlier filter switch (1/0)
integer, intent(in)          :: p_hrvppformat                   ! output as hrvpp format (1/0) ! NEW
integer, intent(in)          :: p_outindex_num                  ! number of image outputs
integer, intent(in)          :: p_outindex(p_outindex_num)      ! output images index
integer, intent(in)          :: p_nclasses                      ! number of land cover classes

!---- Read class specific parameters -------------------------------------------
integer, intent(in)          :: landuse(255)                    ! land cover id
double precision, intent(in) :: p_lpbase(255)                   ! parameter for define base level ! NEW
integer, intent(in)          :: p_fillbase(255)                 ! if using base level to fill large gap
integer, intent(in)          :: p_fitmethod(255)                ! fitting method
double precision, intent(in) :: p_smooth(255)                   ! smoothing parameters
integer, intent(in)          :: p_nenvi(255)                    ! number of envelope iterations
double precision, intent(in) :: p_wfactnum(255)                 ! adaptation strength   
integer, intent(in)          :: p_seasonmethod(255)             ! season detection method (1/2) 1: spline; 2: sinusoidal
double precision, intent(in) :: p_seapar(255)                   ! parameter for find more/less 0/1 season ! NEW
integer, intent(in)          :: p_startmethod(255)              ! method for season start
double precision, intent(in) :: p_startcutoff(255,2)            ! parameter for season start

!---- Outputs -----------------------------------------------------------------

real*4,           intent(out), dimension(row,col,nyr*2*13)       :: phenologicalpar
integer,          intent(out), dimension(row,col,nyr*2)          :: phenologicalparqa
integer,          intent(out), dimension(row,col,nyr)            :: numseasonineachyear
real*4,           intent(out), dimension(row,col,p_outindex_num) :: yfit
integer,          intent(out), dimension(row,col,p_outindex_num) :: yfitqa
real*4,           intent(out), dimension(p_outindex_num)         :: seasonfit
double precision, intent(out), dimension(nimg)                   :: tseq

if (p_printflag==1) then
    write(*,*) 'nyr = ', nyr
    write(*,*) 'p_nclasses = ', p_nclasses
    write(*,*) 'landuse = ', landuse
    write(*,*) 'p_ignoreday = ', p_ignoreday
    write(*,*) 'p_ylu = ', p_ylu
    write(*,*) 'p_fitmethod = ', p_fitmethod
    write(*,*) 'p_smooth = ', p_smooth
    write(*,*) 'p_nodata = ', p_nodata
    write(*,*) 'p_nenvi = ', p_nenvi
    write(*,*) 'p_wfactnum = ', p_wfactnum
    write(*,*) 'p_startmethod = ', p_startmethod
    write(*,*) 'p_startcutoff = ', p_startcutoff
    write(*,*) 'p_lpbase = ', p_lpbase
    write(*,*) 'p_fillbase = ', p_fillbase
    write(*,*) 'p_hrvppformat = ', p_hrvppformat
    write(*,*) 'p_seasonmethod = ', p_seasonmethod
    write(*,*) 'p_seapar = ', p_seapar
    write(*,*) 'nimg = ', nimg
end if
!write(*,*) p_startcutoff(1:2,1:2)
call tsfprocess(nyr,vi,qa,td,lc,p_nclasses,landuse,p_outindex, &
  p_ignoreday,p_ylu,p_printflag,p_fitmethod,p_smooth,p_nodata,p_outlier,p_nenvi,p_wfactnum, &
  p_startmethod,p_startcutoff,p_lpbase,p_fillbase,p_hrvppformat,p_seasonmethod,p_seapar, &
  phenologicalpar, phenologicalparqa, numseasonineachyear, yfit, yfitqa, seasonfit, tseq, &
  row, col, nimg, p_outindex_num)


end subroutine tsf2py

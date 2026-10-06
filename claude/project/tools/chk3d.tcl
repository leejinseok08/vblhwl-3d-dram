# chk3d.tcl — numbers from a 3D Cho-cell mesh for the check against the paper before any run:
# net doping along the channel (cut plane z = CHK_Z, line y = CHK_Y), across the rows (cut plane y = CHK_Y, line x = CHK_X),
# and what lies at the main-gate level across the rows (cut plane y = CHK_YG, line x = CHK_X: the gate metal is a contact
# and has no mesh, so points appear only where the word line is interrupted).
#   CHK_TDR=<mesh.tdr> CHK_Y=0.05 CHK_Z=0.025 CHK_X=0.1 CHK_YG=0.075 CHK_OUTH=<csv> CHK_OUTW=<csv> CHK_OUTG=<csv> svisual -b chk3d.tcl
set d [load_file $env(CHK_TDR)]
set p [create_plot -dataset $d]
puts "REGIONS: [list_regions -plot $p]"
set cz [create_cutplane -plot $p -type z -at $env(CHK_Z)]
set pz [create_plot -dataset $cz]
set h [create_cutline -plot $pz -type y -at $env(CHK_Y)]
export_variables {X DopingConcentration} -dataset $h -filename $env(CHK_OUTH) -overwrite
set cy [create_cutplane -plot $p -type y -at $env(CHK_Y)]
set py [create_plot -dataset $cy]
if {[catch {
  set w [create_cutline -plot $py -type x -at $env(CHK_X)]
  export_variables {Z DopingConcentration} -dataset $w -filename $env(CHK_OUTW) -overwrite
} err]} { puts "WIDTH CUT FAILED: $err" }
if {[info exists env(CHK_YG)]} {
  if {[catch {
    set cg [create_cutplane -plot $p -type y -at $env(CHK_YG)]
    set pg [create_plot -dataset $cg]
    set g [create_cutline -plot $pg -type x -at $env(CHK_X)]
    export_variables {Z DopingConcentration} -dataset $g -filename $env(CHK_OUTG) -overwrite
  } err]} { puts "GATE-LEVEL CUT: nothing there ($err)" }
}
exit

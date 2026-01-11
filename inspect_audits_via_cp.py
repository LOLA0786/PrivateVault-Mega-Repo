from control_plane_audit_reader import read_recent_audits

for a in read_recent_audits(10):
    print(a)

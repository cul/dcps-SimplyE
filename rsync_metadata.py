# Sync OPDS from service to prod/test
import dcps_utils as util


# TODO: Permissions issue needs to be resolved for this to work.

print("====== Syncing opds files ... ======")
print(" ")

fromPath = "/cul/cul0/ldpd/simplye/opds/"
toPath = "ldpdserv@ldpd-nginx-test1:/opt/passenger/ldpd/ebooks_test/shared/public/static-feeds/test/"

myOptions = "--exclude '*.pickle' --exclude '*.zip' --exclude '*test*' --exclude '_archive'"

x = util.rsync_process(fromPath, toPath, myOptions)
print(x)

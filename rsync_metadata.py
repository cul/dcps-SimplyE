import dcps_utils as util


def main():

    ################################
    #
    # Rsync files from web application to storage directory
    #
    ################################

    print("====== Syncing opds files ... ======")
    print(" ")

    fromPath = "/cul/cul0/ldpd/simplye/opds"
    toPath = "ldpd-nginx-test1:/opt/passenger/ldpd/ebooks_test/shared/public/static-feeds/test/"

    myOptions = "--exclude '*.pickle' --exclude '*.zip' --exclude '*test*' --exclude '_archive'"

    x = util.rsync_process(fromPath, toPath, myOptions)
    print(x)

    print(" ")


# Functions go here


if __name__ == "__main__":
    main()

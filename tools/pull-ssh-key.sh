#!/bin/bash

DEFAULT_AWS_PROFILE=blog
AWS_PROFILE=${AWS_PROFILE:-$DEFAULT_AWS_PROFILE}
SCRIPTDIR=$(dirname $(realpath ${BASH_SOURCE[@]}))
KEY_OUTFILE=$SCRIPTDIR/mykey.pem

if [[ -f $KEY_OUTFILE ]]; then
    echo "$KEY_OUTFILE already exists"
    exit 0
fi

get_keypair_names() {
    aws --profile $AWS_PROFILE ssm describe-parameters \
        | egrep 'Name.*/ec2/keypair' \
        | awk '{print $2}' \
        | tr -d \",
}

keypairs=($(get_keypair_names))
if [[ ${#keypairs[@]} -ne 1 ]]; then
    echo "found ${#keypairs[@]} keypairs, expected 1"
    for kp in ${keypairs[@]}; do
        echo "    $kp"
    done
fi
keypair=${keypairs[0]}

aws --profile $AWS_PROFILE ssm get-parameter \
    --name ${keypairs[0]} --with-decryption \
    --query "Parameter.Value" \
    --output text \
        > $KEY_OUTFILE

chmod 0400 $KEY_OUTFILE
echo "wrote $KEY_OUTFILE"

#aws --profile blog ssm get-parameter --name <keyname> --with-decryption --query "Parameter.Value" --output text > mykey.pem
#chmod 400 mykey.pem

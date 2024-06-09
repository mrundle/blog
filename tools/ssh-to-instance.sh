#!/bin/bash -eu

DEFAULT_AWS_PROFILE=blog
AWS_PROFILE=${AWS_PROFILE:-$DEFAULT_AWS_PROFILE}
SCRIPTDIR=$(dirname $(realpath ${BASH_SOURCE[@]}))
SSH_KEY=$SCRIPTDIR/mykey.pem

get_instance_public_dns_names() {
    aws --profile blog ec2 describe-instances \
        --filters "Name=instance-state-name,Values=running" \
        --query 'Reservations[*].Instances[*].[PublicDnsName]' \
        --output text
}

if ! [[ -f $SSH_KEY ]]; then
    echo "ssh key not found, pulling.."
    $SCRIPTDIR/pull-ssh-key.sh
fi

instances=($(get_instance_public_dns_names))
if [[ ${#instances[@]} -eq 0 ]]; then
    echo "couldn't find any instances"
    exit 1
elif [[ ${#instances[@]} -gt 1 ]]; then
    echo "found multiple instances, picking the first"
fi
ssh -i $SSH_KEY ec2-user@${instances[0]}

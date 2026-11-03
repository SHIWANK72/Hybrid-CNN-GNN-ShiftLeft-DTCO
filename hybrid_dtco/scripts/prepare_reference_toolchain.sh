#!/usr/bin/env bash
set -euo pipefail

# Export/import a single filesystem layer: Docker vfs otherwise multiplies disk
# usage across the upstream image's many build layers. No source is changed.
source_digest=sha256:5849e1dde67ba70b36194cf90a172d6c0e4cb2cf5502d6e0dd7c1d251a6d4584
image=dtco/orfs:reference-5849e1dde67b
tools_dir=${DTCO_TOOLS_DIR:-/workspace/.tools}
docker_cmd=(env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH docker --host=unix:///var/run/docker.sock)
if "${docker_cmd[@]}" image inspect "$image" >/dev/null 2>&1; then
    actual=$("${docker_cmd[@]}" image inspect "$image" --format '{{index .Config.Labels "org.dtco.upstream.digest"}}')
    [[ "$actual" == "$source_digest" ]] || { echo 'Toolchain source label mismatch' >&2; exit 1; }
    exit 0
fi
mkdir -p "$tools_dir/crane"
if [[ ! -x "$tools_dir/crane/crane" ]]; then
    curl --fail --location --silent --show-error --max-time 120 \
        https://github.com/google/go-containerregistry/releases/download/v0.20.6/go-containerregistry_Linux_x86_64.tar.gz \
        -o "$tools_dir/crane/release.tar.gz"
    echo "c1d593d01551f2c9a3df5ca0a0be4385a839bd9b86d4a76e18d7b17d16559127  $tools_dir/crane/release.tar.gz" | sha256sum --check
    tar -xzf "$tools_dir/crane/release.tar.gz" -C "$tools_dir/crane" crane
fi
# Reuse a retained, checksummed export after a cloud restart.
if [[ -f "$tools_dir/orfs-rootfs.tar.gz" && -f "$tools_dir/orfs-rootfs.sha256" && -f "$tools_dir/orfs-rootfs.source-digest" ]] \
    && [[ "$(cat "$tools_dir/orfs-rootfs.source-digest")" == "$source_digest" ]]; then
    sha256sum --check "$tools_dir/orfs-rootfs.sha256"
else
    # The registry manifest digest pins and verifies the toolchain contents.
    "$tools_dir/crane/crane" export "registry-1.docker.io/openroad/orfs@$source_digest" - | gzip -1 > "$tools_dir/orfs-rootfs.tar.gz.partial"
    gzip --test "$tools_dir/orfs-rootfs.tar.gz.partial"
    mv "$tools_dir/orfs-rootfs.tar.gz.partial" "$tools_dir/orfs-rootfs.tar.gz"
    sha256sum "$tools_dir/orfs-rootfs.tar.gz" > "$tools_dir/orfs-rootfs.sha256"
    printf '%s\n' "$source_digest" > "$tools_dir/orfs-rootfs.source-digest"
fi
"${docker_cmd[@]}" import \
    --change "LABEL org.dtco.upstream.digest=$source_digest" \
    --change 'WORKDIR /OpenROAD-flow-scripts' \
    --change 'CMD ["/bin/bash"]' \
    "$tools_dir/orfs-rootfs.tar.gz" "$image"

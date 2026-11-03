#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd "$(dirname "$0")/.." && pwd)
lab_dir=${1:?Usage: bash scripts/run_lab_validation.sh NEW_OUTPUT_DIRECTORY}
python_exe=${DTCO_PYTHON:-/workspace/.venvs/dtco/bin/python}
[[ ! -e "$lab_dir" ]] || { echo 'Choose a new output directory; existing evidence is preserved.' >&2; exit 1; }
mkdir -p "$lab_dir"
lab_dir=$(cd "$lab_dir" && pwd)
bash "$project_dir/scripts/prepare_reference_toolchain.sh"
docker_cmd=(env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH docker --host=unix:///var/run/docker.sock)
container_id=$("${docker_cmd[@]}" run --detach --network=none --cpus=2 --memory=8g \
    --user "$(id -u):$(id -g)" \
    --mount "type=bind,src=$project_dir,dst=/project,readonly" \
    --mount "type=bind,src=$lab_dir,dst=/work" --workdir /work \
    dtco/orfs:reference-5849e1dde67b bash -c 'exec sleep infinity')
trap '"${docker_cmd[@]}" rm --force "$container_id" >/dev/null' EXIT
"$python_exe" "$project_dir/scripts/generate_lab_corpus.py" --container "$container_id" --output "$lab_dir"
"$python_exe" -m hybrid_dtco.lab pack --corpus "$lab_dir" --output "$lab_dir/dataset"
"$python_exe" -m hybrid_dtco.lab train --dataset "$lab_dir/dataset" --output "$lab_dir/training"
"$python_exe" -m hybrid_dtco.lab evaluate --dataset "$lab_dir/dataset" --checkpoint "$lab_dir/training/model.pt" --output "$lab_dir/evaluation"
"$python_exe" "$project_dir/scripts/check_lab_service.py" --root "$lab_dir"
(cd "$project_dir" && "$python_exe" -m pytest -p no:cacheprovider --junitxml="$lab_dir/tests.xml")
"$python_exe" "$project_dir/scripts/build_lab_report.py" --root "$lab_dir" --tests "$lab_dir/tests.xml"
printf 'Evidence directory: %s\n' "$lab_dir"

export default (_, inject) => {
  const exportCSV = (data, filename) => {
    const csvContent = "data:text/csv;charset=utf-8," +
      data.map(row => 
        Object.values(row)
          .map(value => {
            if (typeof value === 'number') {
              return value.toFixed(2).toString().replace('.', ',')
            }
            return `"${value.toString().replace(/"/g, '""')}"`
          })
          .join(';')
      ).join('\n')

    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", filename)
    document.body.appendChild(link)
    link.click()
  }

  inject('export', { exportCSV })
}